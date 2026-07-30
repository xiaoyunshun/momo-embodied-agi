"""
墨墨 MCP 分身 (MCPAvatar) — 将 MCP 服务器工具包装为墨墨分身

MCP (Model Context Protocol) 是一种标准化的工具调用协议。
通过 MCPAvatar，任何符合 MCP 标准的服务器都自动成为墨墨的一个分身。

支持两种传输方式：
1. HTTP/StreamableHTTP — 远程 MCP 服务器 (POST JSON-RPC)
2. Stdio — 本地子进程 MCP 服务器 (stdin/stdout JSON-RPC)

用法:
    from momo.mcp_avatar import MCPAvatar

    # HTTP 模式
    mcp = MCPAvatar("weather", url="http://localhost:8080/mcp")
    mcp.connect()
    runner.register_avatar("weather_mcp", mcp)

    # Stdio 模式（需要 mcp 包）
    mcp = MCPAvatar("filesystem", command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"])
    mcp.connect()
    runner.register_avatar("fs", mcp)
"""

import json
import subprocess
import threading
import sys
from typing import Optional


# ──────────────────────────────────────────
# MCP JSON-RPC 消息构建
# ──────────────────────────────────────────


def _make_request(method: str, params: dict = None, request_id: int = 1) -> str:
    return json.dumps({
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {},
    })


def _make_notification(method: str, params: dict = None) -> str:
    return json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
    })


# ──────────────────────────────────────────
# MCPAvatar 类
# ──────────────────────────────────────────


class MCPAvatar:
    """包装 MCP 服务器为墨墨分身。

    支持的 MCP 协议版本: 2024-11-05 (initial) / 2025-03-26 (latest)
    """

    def __init__(
        self,
        server_name: str,
        url: str = None,
        command: str = None,
        args: list = None,
        headers: dict = None,
    ):
        self.name = f"MCP:{server_name}"
        self.server_name = server_name
        self.url = url
        self.command = command
        self.args = args or []
        self.headers = headers or {}
        self.tools = {}  # tool_name -> {description, inputSchema}
        self.connected = False
        self._request_id = 0
        self._http_session = None
        self._process = None
        self._read_thread = None
        self._lock = threading.Lock()

    def connect(self, timeout: float = 10.0) -> dict:
        """连接到 MCP 服务器并发现可用工具"""
        self._request_id = 0

        if self.url:
            return self._connect_http(timeout)
        elif self.command:
            return self._connect_stdio(timeout)
        else:
            return {"status": "failed", "error": "需要 url (HTTP) 或 command (Stdio)"}

    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self._process:
            try:
                self._process.terminate()
                self._process = None
            except Exception:
                pass
        for name in list(self.tools.keys()):
            del self.tools[name]

    def process(self, text: str) -> dict:
        """将输入路由到最合适的 MCP 工具"""
        if not self.connected or not self.tools:
            return {"response": "", "confidence": 0.0}

        # 简单关键词匹配: 找出 text 与工具描述最相关的
        best_tool = None
        best_score = 0
        text_lower = text.lower()

        for tool_name, tool_info in self.tools.items():
            desc = (tool_info.get("description", "") + " " + tool_name).lower()
            # 计算关键词命中数
            score = sum(1 for word in text_lower.split() if word in desc)
            if score > best_score:
                best_score = score
                best_tool = tool_name

        if best_tool and best_score > 0:
            return self._call_tool(best_tool, {"text": text})
        else:
            return {"response": "", "confidence": 0.0}

    def help(self) -> dict:
        """返回可用工具列表"""
        return {
            "name": self.name,
            "description": f"MCP 服务器: {self.server_name}",
            "tools": list(self.tools.keys()),
            "connected": self.connected,
        }

    # ────────── HTTP 传输 ──────────

    def _connect_http(self, timeout: float) -> dict:
        """通过 HTTP 连接 MCP 服务器"""
        try:
            import urllib.request
            import urllib.error
        except ImportError:
            return {"status": "failed", "error": "urllib 不可用"}

        # 1. 初始化 — 发送 initialize 请求
        result = self._http_request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "momo-avatar", "version": "1.0.0"},
        }, timeout)

        if not result.get("result"):
            return {"status": "failed", "error": "MCP 初始化失败"}

        # 2. 发送 initialized 通知
        self._http_notify("notifications/initialized")

        # 3. 发现工具
        tools_result = self._http_request("tools/list", {}, timeout)
        tools_list = tools_result.get("result", {}).get("tools", [])

        for tool in tools_list:
            self.tools[tool["name"]] = {
                "description": tool.get("description", ""),
                "inputSchema": tool.get("inputSchema", {}),
            }

        self.connected = True
        return {
            "status": "connected",
            "tools_found": len(self.tools),
            "tools": list(self.tools.keys()),
        }

    def _http_request(self, method: str, params: dict, timeout: float) -> dict:
        import urllib.request
        import urllib.error

        with self._lock:
            self._request_id += 1
            req_id = self._request_id

        body = _make_request(method, params, req_id)
        data = body.encode("utf-8")

        req = urllib.request.Request(
            self.url,
            data=data,
            headers={
                "Content-Type": "application/json",
                **self.headers,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def _http_notify(self, method: str, params: dict = None):
        """发送通知（无响应期望）"""
        import urllib.request

        body = _make_notification(method, params)
        data = body.encode("utf-8")

        req = urllib.request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json", **self.headers},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass

    # ────────── Stdio 传输 ──────────

    def _connect_stdio(self, timeout: float) -> dict:
        """通过 Stdio 子进程连接 MCP 服务器"""
        if not self.command:
            return {"status": "failed", "error": "未指定 command"}

        try:
            import shlex
            self._process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError as e:
            return {"status": "failed", "error": f"命令未找到: {e}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

        # 启动读取线程
        self._read_thread = threading.Thread(
            target=self._stdio_read_loop, daemon=True
        )
        self._read_thread.start()

        # 发送 initialize
        result = self._stdio_request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "momo-avatar", "version": "1.0.0"},
        }, timeout)

        if "error" in result:
            return {"status": "failed", "error": str(result["error"])}

        # 发送 initialized 通知
        self._stdio_notify("notifications/initialized")

        # 发现工具
        tools_result = self._stdio_request("tools/list", {}, timeout)
        tools_list = tools_result.get("tools", [])

        for tool in tools_list:
            self.tools[tool["name"]] = {
                "description": tool.get("description", ""),
                "inputSchema": tool.get("inputSchema", {}),
            }

        self.connected = True
        return {
            "status": "connected",
            "tools_found": len(self.tools),
            "tools": list(self.tools.keys()),
        }

    def _stdio_request(self, method: str, params: dict, timeout: float) -> dict:
        with self._lock:
            self._request_id += 1
            req_id = self._request_id

        body = _make_request(method, params, req_id)

        if self._process and self._process.stdin:
            self._process.stdin.write(body + "\n")
            self._process.stdin.flush()

        # 读取响应（阻塞）
        if self._process and self._process.stdout:
            line = self._process.stdout.readline()
            if line:
                return json.loads(line.strip())
        return {"error": "无响应"}

    def _stdio_notify(self, method: str, params: dict = None):
        with self._lock:
            body = _make_notification(method, params) + "\n"
            if self._process and self._process.stdin:
                self._process.stdin.write(body)
                self._process.stdin.flush()

    def _stdio_read_loop(self):
        """后台读取 stdout 中的通知消息"""
        while self.connected and self._process and self._process.stdout:
            try:
                line = self._process.stdout.readline()
                if not line:
                    break
                # 通知类消息忽略
            except Exception:
                break

    # ────────── 调用工具 ──────────

    def _call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用 MCP 工具"""
        if self.url:
            result = self._http_request("tools/call", {
                "name": tool_name,
                "arguments": arguments,
            }, timeout=30)
        elif self._process:
            result = self._stdio_request("tools/call", {
                "name": tool_name,
                "arguments": arguments,
            }, timeout=30)
        else:
            return {"response": "未连接", "confidence": 0.0}

        # 提取 content
        content = result.get("result", {}).get("content", [])
        text_parts = [
            c.get("text", "") for c in content if c.get("type") == "text"
        ]

        if text_parts:
            return {"response": "\n".join(text_parts), "confidence": 0.8}
        return {"response": str(result), "confidence": 0.5}

    def __del__(self):
        self.disconnect()
