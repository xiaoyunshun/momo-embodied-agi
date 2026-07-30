"""
墨墨运行器 (MomoRunner) — 核心调度框架

封装了 MomoCore、MomoDaemon 和分身系统的启动/停止逻辑，
供外部应用和 pip 包使用。

用法:
    from momo.runner import MomoRunner
    
    # 极简模式
    runner = MomoRunner()
    runner.start()
    
    # 注册自定义分身
    runner.register_avatar("my_skill", MyAvatar())
    
    # 交互
    response = runner.interact("你好，墨墨")
"""

import sys
import os
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable, Dict, Any


BEIJING_TZ = timezone(timedelta(hours=8))


class MomoRunner:
    """墨墨运行器 — 一键启动完整具身智能系统。

    不依赖 Hermes / LangChain / 任何第三方运行环境。
    只需 Python 3.10+。
    """

    def __init__(self, xiaoge_name: str = "用户", data_dir: str = None):
        self.name = xiaoge_name
        self.data_dir = Path(data_dir or Path.home() / ".momo")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 核心实例 (延迟加载)
        self.core = None
        self.brainstem = None
        self.cortex = None
        self.memory = None
        self.senses = {}
        self.avatars = {}

        # 守护线程
        self._daemon_running = False
        self._daemon_thread = None
        self._heartbeat_count = 0

        # 状态
        self.born_at = None
        self.interaction_count = 0

        # 注册内置感官
        self._register_builtin_senses()

    # ──────────────────────────────
    # 启动 / 停止
    # ──────────────────────────────

    def start(self) -> dict:
        """启动墨墨"""
        if self.core:
            return {"status": "already_running"}

        try:
            self._init_core()
            self._start_daemon()
            self.born_at = time.time()
            return {
                "status": "started",
                "message": f"{self.name}的墨墨已启动",
                "uptime": time.time() - self.born_at,
            }
        except ImportError as e:
            return {"status": "failed", "error": f"导入错误: {e}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def stop(self) -> dict:
        """停止墨墨"""
        self._daemon_running = False
        return {
            "status": "stopped",
            "heartbeats": self._heartbeat_count,
            "interactions": self.interaction_count,
        }

    def status(self) -> dict:
        """当前状态"""
        uptime = time.time() - self.born_at if self.born_at else 0
        return {
            "running": self._daemon_running,
            "uptime_seconds": round(uptime, 1),
            "heartbeats": self._heartbeat_count,
            "interactions": self.interaction_count,
            "avatars": list(self.avatars.keys()),
            "senses": list(self.senses.keys()),
            "message": "墨墨在运行中" if self._daemon_running else "墨墨未启动",
        }

    # ──────────────────────────────
    # 交互
    # ──────────────────────────────

    def interact(self, text: str) -> dict:
        """一次完整的交互循环"""
        self.interaction_count += 1
        start = time.time()

        # 1) 感知
        perception = self._perceive(text)

        # 2) 推理 (如果 cortex 已加载)
        reasoning = {}
        if self.cortex:
            reasoning = self._reason(perception)

        # 3) 选择分身
        avatar_response = self._route_to_avatar(perception, reasoning)

        elapsed = time.time() - start
        return {
            "response": avatar_response.get("response", ""),
            "avatar": avatar_response.get("avatar", "core"),
            "perception": perception,
            "reasoning": reasoning,
            "elapsed_seconds": round(elapsed, 3),
            "interaction": self.interaction_count,
        }

    # ──────────────────────────────
    # 分身注册
    # ──────────────────────────────

    def register_avatar(self, name: str, avatar_instance) -> bool:
        """注册一个自定义分身

        avatar_instance 需要实现：
            process(input_data) -> dict
            help() -> dict  (可选)
        """
        self.avatars[name] = avatar_instance
        return True

    def register_sense(self, name: str, sense_instance) -> bool:
        """注册一个自定义感官"""
        self.senses[name] = sense_instance
        return True

    # ──────────────────────────────
    # 内部：核心初始化
    # ──────────────────────────────

    def _init_core(self):
        """延迟初始化核心模块"""
        # 尝试导入内置核心模块 —— 优雅降级
        try:
            sys.path.insert(
                0, str(Path(__file__).parent.parent / "code" / "核心模块")
            )
            from momo_cortex import MomoCortex
            from momo_brainstem import MomoBrainstem

            self.cortex = MomoCortex()
            self.brainstem = MomoBrainstem()
        except ImportError:
            # 没有 cortex 时使用回退
            self.cortex = None
            self.brainstem = None

        self.core = True  # 标记核心已初始化

    def _register_builtin_senses(self):
        """注册内置感官桩（轻量回退）"""
        self.senses["text"] = TextSense()

    def _perceive(self, text: str) -> dict:
        """感知输入"""
        result = {"raw": text, "senses": {}}
        for name, sense in self.senses.items():
            try:
                result["senses"][name] = sense.process(text)
            except Exception as e:
                result["senses"][name] = {"error": str(e)}
        return result

    def _reason(self, perception: dict) -> dict:
        """用 cortex 推理"""
        if not self.cortex:
            return {"mode": "bypass"}
        try:
            return self.cortex.process(perception)
        except Exception as e:
            return {"error": str(e)}

    def _route_to_avatar(self, perception: dict, reasoning: dict) -> dict:
        """将输入路由到最合适的分身"""
        text = perception.get("raw", "")

        # 先问已注册分身是否能处理
        for name, avatar in self.avatars.items():
            try:
                result = avatar.process(text)
                if result and result.get("response"):
                    return {"response": result["response"], "avatar": name}
            except Exception:
                continue

        # 没有合适分身时返回通用回应
        return {
            "response": f"收到。交互 #{self.interaction_count}",
            "avatar": "core",
        }

    # ──────────────────────────────
    # 内部：守护进程
    # ──────────────────────────────

    def _start_daemon(self):
        self._daemon_running = True
        self._daemon_thread = threading.Thread(
            target=self._daemon_loop, daemon=True
        )
        self._daemon_thread.start()

    def _daemon_loop(self):
        """后台心跳循环"""
        while self._daemon_running:
            try:
                self._heartbeat()
                time.sleep(10)
            except Exception:
                time.sleep(30)

    def _heartbeat(self):
        self._heartbeat_count += 1
        (self.data_dir / "heartbeat.json").write_text(
            json.dumps(
                {
                    "last_beat": datetime.now(BEIJING_TZ).isoformat(),
                    "total_beats": self._heartbeat_count,
                    "status": "alive",
                },
                ensure_ascii=False,
            )
        )


# ──────────────────────────────
# 内置轻量感官
# ──────────────────────────────


class TextSense:
    """文本感官 — 最小可行实现"""

    def process(self, text: str) -> dict:
        return {
            "type": "text",
            "length": len(text),
            "words": len(text.split()),
            "has_question": "?" in text or "？" in text,
        }


# ──────────────────────────────
# CLI 入口
# ──────────────────────────────


def main():
    """命令行启动"""
    import argparse

    parser = argparse.ArgumentParser(description="墨墨 (Momo) — 开源具身智能框架")
    parser.add_argument("--name", default="用户", help="你的名字")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="交互式模式"
    )
    args = parser.parse_args()

    runner = MomoRunner(xiaoge_name=args.name)
    result = runner.start()
    print(f"🧠 {result['message']}")

    if args.interactive:
        print("\n输入 'exit' 退出，输入 'status' 查看状态\n")
        while True:
            try:
                text = input(">>> ")
                if text.lower() in ("exit", "quit", "q"):
                    break
                if text.lower() == "status":
                    print(json.dumps(runner.status(), ensure_ascii=False, indent=2))
                    continue
                resp = runner.interact(text)
                print(f"墨墨: {resp['response']}")
            except (KeyboardInterrupt, EOFError):
                break

    runner.stop()
    print("🛑 墨墨已停止")


if __name__ == "__main__":
    main()
