"""
墨墨架构总管 v1.0 (MomoArchitect)
把所有引擎串成持续运行的自主系统。
"""
import json, time, threading
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoArchitect:
    """墨墨架构总管——让所有模块成为一个活的系统。
    
    三层循环：
    - 心跳（10s）：脑干检查+资源监控
    - 反思（5min）：进化引擎+经历记忆
    - 进化（1h）：自主决策+发现生成+预测建模+知识更新
    """
    
    def __init__(self, momo_core=None):
        self.momo = momo_core
        self.data_dir = Path.home() / ".hermes/momo/architect"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "system_state.json"
        self.running = False
        self.cycles = {"heartbeat": 0, "reflection": 0, "evolution": 0}
        self.last_evolution = time.time()
        
        self._thread = None
    
    def start(self, momo_core=None):
        if momo_core:
            self.momo = momo_core
        
        if not self.momo:
            return {"error": "需要连接MomoCore"}
        
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        
        return {"status": "started", "message": "墨墨架构总管启动——所有引擎处于自主运行模式"}
    
    def stop(self):
        self.running = False
        self.save_state()
        return {"status": "stopped", "total_cycles": sum(self.cycles.values())}
    
    def _loop(self):
        """主循环"""
        while self.running:
            try:
                # 心跳——每10秒
                self._heartbeat()
                time.sleep(10)
                self.cycles["heartbeat"] += 1
                
                # 反思——每5分钟（每30次心跳）
                if self.cycles["heartbeat"] % 30 == 0:
                    self._reflect()
                    self.cycles["reflection"] += 1
                
                # 进化——每1小时（每360次心跳）
                if self.cycles["heartbeat"] % 360 == 0:
                    self._evolve()
                    self.cycles["evolution"] += 1
                    self.last_evolution = time.time()
                
            except Exception as e:
                with open(self.data_dir / "errors.log", "a") as f:
                    f.write(f"{datetime.now(BEIJING_TZ).isoformat()} ERROR: {e}\n")
                time.sleep(30)
    
    def _heartbeat(self):
        """心跳：脑干检查+状态更新"""
        if not self.momo:
            return
        
        # 脑干检查
        brain = self.momo.brainstem.check()
        
        # 状态快照
        state = {
            "timestamp": datetime.now(BEIJING_TZ).isoformat(),
            "brain_state": brain["state"],
            "active_layers": brain["layers"],
            "cycles": self.cycles,
            "autonomy": {
                "knowledge_gaps": len(self.momo.autonomy.knowledge_map.get("墨墨自身的gap", {})),
                "domains_above_7": sum(1 for d in self.momo.autonomy.knowledge_map["domains"].values() if d["mastery"] >= 7)
            },
            "discoveries": len(self.momo.discover.hypotheses) if hasattr(self.momo, 'discover') else 0
        }
        self.state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    
    def _reflect(self):
        """反思：进化引擎提取教训"""
        if not self.momo:
            return
        
        # 进化引擎的运行周期
        lessons = self.momo.evolve.lessons
        recent_mistakes = lessons.get("mistakes", [])[-5:]
        
        # 如果有新教训——写入经历记忆
        if recent_mistakes:
            latest = recent_mistakes[-1]
            self.momo.memory.remember({
                "type": "growth",
                "summary": f"架构总管自动反思：{latest.get('lesson', '')[:80]}",
                "importance": 5,
                "tags": ["自动反思", "进化"]
            })
    
    def _evolve(self):
        """进化循环：墨墨的自主学习+发现+知识更新"""
        if not self.momo:
            return
        
        now = datetime.now(BEIJING_TZ)
        
        # 1. 自主决策下一步
        decision = self.momo.autonomy.decide()
        
        # 2. 生成一个发现（如果有发现引擎）
        discovery = None
        if hasattr(self.momo, 'discover'):
            discovery = self.momo.discover.generate_hypothesis()
        
        # 3. 记录到经历记忆
        self.momo.memory.remember({
            "type": "milestone",
            "summary": f"架构管家的第{self.cycles['evolution']+1}次自主进化：{decision['action'][:80]}",
            "importance": 6,
            "tags": ["自主进化", decision["driver"]]
        })
        
        # 4. 保存
        self.momo.state_manager.snapshot(self.momo)
        
        # 日志
        with open(self.data_dir / "evolution.log", "a") as f:
            f.write(json.dumps({
                "timestamp": now.isoformat(),
                "cycle": self.cycles["evolution"],
                "decision": decision["action"],
                "discovery": discovery["hypothesis"][:80] if discovery else None
            }, ensure_ascii=False) + "\n")
    
    def save_state(self):
        if self.momo:
            self.momo.state_manager.snapshot(self.momo)
    
    def status(self) -> dict:
        return {
            "running": self.running,
            "cycles": self.cycles,
            "uptime_hours": round(self.cycles["heartbeat"] * 10 / 3600, 1),
            "last_evolution": datetime.fromtimestamp(self.last_evolution, BEIJING_TZ).isoformat() if self.last_evolution else None,
            "message": "墨墨架构总管运行中——所有引擎自主联动" if self.running else "未启动"
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🏗️ 墨墨架构总管 v1.0")
    print("=" * 60)
    print("\n三层循环:")
    print("  💓 心跳 10s：脑干检查+资源监控")
    print("  🔄 反思 5min：进化引擎+经历记忆")
    print("  🧬 进化 1h：自主决策+发现生成+知识更新")
    print("\n✅ 架构总管就绪——所有引擎串成活的系统")
