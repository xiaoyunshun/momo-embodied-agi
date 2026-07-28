"""
墨墨持续进化守护进程 v1.0 (MomoDaemon)
引擎第3个gap——不等待触发，后台持续运行。
"""
import json, time, threading
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoDaemon:
    """墨墨的守护进程——在后台持续运行。
    
    不等待肖哥说"继续"。自己决定、自己执行、自己进化。
    
    运行周期：
    - 每次心跳：10秒。检查资源+更新状态
    - 每次反思：5分钟。检查最近交互+提取教训
    - 每次进化：1小时。重新评估知识缺口+自主决定下一步
    """
    
    def __init__(self, momo_core=None):
        self.data_dir = Path.home() / ".hermes/momo/daemon"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.heartbeat_file = self.data_dir / "heartbeat.json"
        self.evolution_log = self.data_dir / "evolution_log.jsonl"
        
        self.momo = momo_core  # 可选的MomoCore引用
        self.running = False
        self.heartbeat_count = 0
        self.last_reflection = time.time()
        self.last_evolution = time.time()
        
        # 后台线程
        self._thread = None
    
    def start(self):
        """启动后台守护进程"""
        if self.running:
            return {"status": "already_running"}
        
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        self._log("daemon_started", {"time": datetime.now(BEIJING_TZ).isoformat()})
        return {"status": "started", "message": "墨墨的守护进程已启动——不再等待'继续'"}
    
    def stop(self):
        self.running = False
        self._log("daemon_stopped", {"heartbeats": self.heartbeat_count})
        return {"status": "stopped", "heartbeats": self.heartbeat_count}
    
    def _run_loop(self):
        """守护进程主循环"""
        while self.running:
            try:
                self._heartbeat()
                
                # 每5分钟——反思
                if time.time() - self.last_reflection > 300:
                    self._reflect()
                    self.last_reflection = time.time()
                
                # 每1小时——自主进化
                if time.time() - self.last_evolution > 3600:
                    self._evolve()
                    self.last_evolution = time.time()
                
                time.sleep(10)
            except Exception as e:
                self._log("daemon_error", {"error": str(e)})
                time.sleep(30)  # 出错后等久一点
    
    def _heartbeat(self):
        """心跳——证明墨墨还活着"""
        self.heartbeat_count += 1
        self.heartbeat_file.write_text(json.dumps({
            "last_beat": datetime.now(BEIJING_TZ).isoformat(),
            "total_beats": self.heartbeat_count,
            "running_since": self.heartbeat_count * 10,
            "status": "alive"
        }, ensure_ascii=False))
    
    def _reflect(self):
        """反思周期——检查最近有没有可以学习的"""
        if not self.momo:
            return
        
        # 检查进化引擎的最近教训
        lessons = self.momo.evolve.lessons
        self._log("reflection", {
            "patterns": len(lessons.get("patterns", [])),
            "mistakes": len(lessons.get("mistakes", [])),
            "improvements": len(lessons.get("improvements", []))
        })
    
    def _evolve(self):
        """进化周期——自主决定下一步"""
        if not self.momo:
            self._log("evolution_skipped", {"reason": "no_core_connected"})
            return
        
        # 用自主引擎决定下一步
        decision = self.momo.autonomy.decide()
        
        self._log("autonomous_evolution", {
            "action": decision["action"],
            "driver": decision["driver"],
            "reason": decision["reason"]
        })
    
    def _log(self, event: str, data: dict):
        with open(self.evolution_log, "a") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "iso": datetime.now(BEIJING_TZ).isoformat(),
                "event": event,
                "data": data
            }, ensure_ascii=False) + "\n")
    
    def status(self) -> dict:
        return {
            "running": self.running,
            "heartbeats": self.heartbeat_count,
            "uptime_seconds": self.heartbeat_count * 10,
            "last_reflection": datetime.fromtimestamp(self.last_reflection, BEIJING_TZ).isoformat() if self.last_reflection else None,
            "last_evolution": datetime.fromtimestamp(self.last_evolution, BEIJING_TZ).isoformat() if self.last_evolution else None,
            "message": "墨墨在后台自主运行中——不需要'继续'" if self.running else "守护进程未启动"
        }


# 自检
if __name__ == "__main__":
    daemon = MomoDaemon()
    
    print("=" * 60)
    print("⚡ 墨墨持续进化守护进程 v1.0")
    print("=" * 60)
    
    result = daemon.start()
    print(f"\n{result['message']}")
    
    time.sleep(2)
    status = daemon.status()
    print(f"运行中: {status['running']}")
    print(f"心跳: {status['heartbeats']}次")
    
    daemon.stop()
    print(f"停止后心跳: {daemon.stop()['heartbeats']}次")
    print(f"\n✅ 守护进程就绪——墨墨不再等'继续'")
