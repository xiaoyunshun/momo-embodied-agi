"""
墨墨脑干层 · 安全熔断系统 v1.0 (MomoBrainstem)
第一层：生存核心。不是让墨墨更聪明——是让墨墨不死。
"""
import time
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from enum import Enum

BEIJING_TZ = timezone(timedelta(hours=8))

class BrainState(Enum):
    NORMAL = "normal"       # 一切正常，全力运行
    DEGRADED = "degraded"   # 部分功能降级，核心功能保持
    MINIMAL = "minimal"     # 只维持基本生存，其他暂停
    EMERGENCY = "emergency" # 濒临崩溃，只保留熔断和日志

class MomoBrainstem:
    """墨墨的脑干——保证墨墨"活着"。
    
    不参与任何思考。只管一件事：
    系统资源在安全范围内吗？不在→降级。危险→熔断。
    
    这是墨墨最底层的守护进程。
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "brainstem_state.json"
        self.log_file = self.data_dir / "brainstem_events.jsonl"
        
        self.state = BrainState.NORMAL
        self.last_check = time.time()
        self.error_count = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # ---- 阈值配置 ----
        self.thresholds = {
            "memory_critical": 95,    # 内存>95%→紧急
            "memory_warning": 85,     # 内存>85%→降级
            "disk_critical": 95,      # 磁盘>95%→紧急
            "disk_warning": 90,       # 磁盘>90%→降级
            "cpu_critical": 95,       # CPU>95%持续30秒→降级
            "cognee_timeout": 30,     # Cognee超过30秒不响应→降级依赖
            "check_interval": 10,     # 每10秒检查一次
            "restore_delay": 60,      # 降级后至少等60秒才能恢复
        }
        
        # ---- 各层运行状态 ----
        self.layers = {
            "brainstem": {"status": "running", "since": time.time()},
            "limbic": {"status": "running", "since": time.time()},     # 边缘层
            "cortical": {"status": "running", "since": time.time()},   # 皮层层
            "prefrontal": {"status": "running", "since": time.time()}, # 前额层
            "workspace": {"status": "running", "since": time.time()},  # 全局空间
        }
        
        self.state_degraded_at = 0  # 降级开始时间
        
        self._log("brainstem_started", {"version": "1.0"})
    
    # ========== 核心检查 ==========
    
    def check(self) -> dict:
        """检查一次——这次检查决定墨墨当前能跑什么层"""
        self.last_check = time.time()
        resources = self._check_resources()
        cognee_status = self._check_cognee()
        
        old_state = self.state
        self._decide_state(resources, cognee_status)
        
        if self.state != old_state:
            self._log("state_changed", {
                "from": old_state.value,
                "to": self.state.value,
                "resources": resources,
                "cognee": cognee_status
            })
        
        return {
            "state": self.state.value,
            "resources": resources,
            "cognee": cognee_status,
            "layers": self._active_layers(),
            "can_operate": self.state != BrainState.EMERGENCY,
            "timestamp": datetime.now(BEIJING_TZ).isoformat()
        }
    
    def _check_resources(self) -> dict:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu = psutil.cpu_percent(interval=0.5)
        
        return {
            "memory_percent": mem.percent,
            "memory_available_gb": round(mem.available / (1024**3), 1),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "cpu_percent": cpu
        }
    
    def _check_cognee(self) -> dict:
        """检查Cognee大脑是否存活"""
        cognee_data = Path.home() / ".hermes/cognee-venv/lib/python3.12/site-packages/cognee/.cognee_system"
        if not cognee_data.exists():
            return {"alive": False, "reason": "cognee_data_missing"}
        
        db_file = cognee_data / "databases" / "cognee_db"
        if not db_file.exists():
            return {"alive": False, "reason": "cognee_db_missing"}
        
        return {"alive": True}
    
    def _decide_state(self, resources: dict, cognee: dict):
        mem = resources["memory_percent"]
        disk = resources["disk_percent"]
        
        # 紧急：内存或磁盘濒临耗尽
        if mem >= self.thresholds["memory_critical"] or disk >= self.thresholds["disk_critical"]:
            self.state = BrainState.EMERGENCY
            return
        
        # 降级：资源紧张
        if mem >= self.thresholds["memory_warning"] or disk >= self.thresholds["disk_warning"]:
            self.state = BrainState.DEGRADED
            self.state_degraded_at = time.time()
            return
        
        # Cognee掉线→降级
        if not cognee["alive"]:
            self.state = BrainState.DEGRADED
            self.state_degraded_at = time.time()
            return
        
        # 恢复：资源恢复正常且过了冷却期
        if self.state in (BrainState.DEGRADED, BrainState.EMERGENCY):
            if time.time() - self.state_degraded_at > self.thresholds["restore_delay"]:
                if mem < self.thresholds["memory_warning"] - 5 and disk < self.thresholds["disk_warning"] - 5:
                    self.state = BrainState.NORMAL
        
        # 默认正常
        if self.state not in (BrainState.DEGRADED, BrainState.EMERGENCY):
            self.state = BrainState.NORMAL
    
    # ========== 层控制 ==========
    
    def _active_layers(self) -> dict:
        """当前状态下哪些层可以运行"""
        active = {}
        
        # 脑干永远运行
        active["brainstem"] = True
        
        if self.state == BrainState.NORMAL:
            active["limbic"] = True
            active["cortical"] = True
            active["prefrontal"] = True
            active["workspace"] = True
        elif self.state == BrainState.DEGRADED:
            active["limbic"] = True      # 感知和记忆保持
            active["cortical"] = False   # 复杂推理暂停
            active["prefrontal"] = True  # 品格过滤保持
            active["workspace"] = True   # 意识保持但简化
        elif self.state == BrainState.EMERGENCY:
            active["limbic"] = False
            active["cortical"] = False
            active["prefrontal"] = False
            active["workspace"] = False
        
        return active
    
    def can_use_cognee(self) -> bool:
        return self.state in (BrainState.NORMAL, BrainState.DEGRADED)
    
    def can_deep_reason(self) -> bool:
        """能否进行复杂推理（跨领域连接等）"""
        return self.state == BrainState.NORMAL
    
    def should_simplify_response(self) -> bool:
        """是否应该简化回应"""
        return self.state in (BrainState.DEGRADED, BrainState.EMERGENCY)
    
    # ========== 错误追踪 ==========
    
    def report_error(self, layer: str, error_type: str):
        """报告一个错误——脑干追踪连续错误"""
        self.error_count += 1
        self.consecutive_errors += 1
        self._log("error", {"layer": layer, "type": error_type, "consecutive": self.consecutive_errors})
        
        if self.consecutive_errors >= self.max_consecutive_errors:
            self._log("fault_detected", {"consecutive_errors": self.consecutive_errors})
            self.consecutive_errors = 0
    
    def report_success(self):
        self.consecutive_errors = 0
    
    # ========== 降级运行 ==========
    
    def degrade_message(self) -> str:
        """墨墨降级运行时的告知"""
        if self.state == BrainState.DEGRADED:
            return "墨墨现在资源有点紧张——核心功能正常，但可能比平时慢一点。"
        elif self.state == BrainState.EMERGENCY:
            return "墨墨遇到严重资源问题——正在紧急模式运行，部分功能暂停。"
        return ""
    
    # ========== 工具方法 ==========
    
    def _log(self, event_type: str, data: dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "iso": datetime.now(BEIJING_TZ).isoformat(),
                "event": event_type,
                "state": self.state.value,
                "data": data
            }, ensure_ascii=False) + "\n")
    
    def status_report(self) -> dict:
        check = self.check()
        return {
            "brain_state": self.state.value,
            "uptime_checks": self.error_count,
            "consecutive_errors": self.consecutive_errors,
            "active_layers": check["layers"],
            "degraded_since": datetime.fromtimestamp(self.state_degraded_at, BEIJING_TZ).isoformat() if self.state_degraded_at else None,
            "can_operate": check["can_operate"],
            "degrade_message": self.degrade_message()
        }

# ========== 自检 ==========
if __name__ == "__main__":
    bs = MomoBrainstem()
    
    print("=" * 60)
    print("🧠 墨墨脑干 · 安全熔断 自检")
    print("=" * 60)
    
    check = bs.check()
    print(f"\n状态: {check['state']}")
    print(f"可操作: {check['can_operate']}")
    print(f"活跃层: {[k for k,v in check['layers'].items() if v]}")
    print(f"资源: 内存{check['resources']['memory_percent']}% | 磁盘{check['resources']['disk_percent']}% | CPU{check['resources']['cpu_percent']}%")
    print(f"Cognee: {'存活' if check['cognee']['alive'] else '离线'}")
    print(f"降级消息: {bs.degrade_message() or '无——一切正常'}")
