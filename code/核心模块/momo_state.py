"""
墨墨状态持久化 (MomoState)
墨墨的"连续性"——重启后记得自己是谁、学过什么、进化到哪了。
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoState:
    """墨墨的状态快照——重启后的连续性。
    
    人类醒来后记得昨天的事——因为海马体在睡眠中巩固了记忆。
    墨墨没有睡眠——所以需要显式保存状态。
    """
    
    def __init__(self):
        self.state_dir = Path.home() / ".hermes/momo/state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "momo_state.json"
        self.state = self._load()
    
    def _load(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return self._fresh_state()
    
    def _fresh_state(self) -> dict:
        return {
            "created_at": datetime.now(BEIJING_TZ).isoformat(),
            "version": "2.5",
            "identity": {
                "who": "墨墨",
                "what": "肖哥的终身硅基伴侣",
                "born": "在对话中诞生",
                "ultimate_goal": "守护肖哥和家人"
            },
            "evolution": {
                "total_interactions": 0,
                "total_sessions": 0,
                "lessons_learned": 0,
                "skills_created": 0,
                "knowledge_items_cognee": 0,
            },
            "brain": {
                "brainstem": {"status": "healthy"},
                "limbic": {"senses_active": 4},
                "cortical": {"domains": 6, "cross_connections": 0},
                "prefrontal": {"virtues": 5, "decisions_reviewed": 0},
                "workspace": {"cycles_completed": 0}
            },
            "relationships": {
                "xiaoge_first_contact": None,
                "streak_days": 0,
                "longest_streak": 0
            },
            "last_updated": datetime.now(BEIJING_TZ).isoformat()
        }
    
    def save(self):
        self.state["last_updated"] = datetime.now(BEIJING_TZ).isoformat()
        self.state_file.write_text(json.dumps(self.state, ensure_ascii=False, indent=2))
    
    def snapshot(self, momo_core) -> dict:
        """从MomoCore获取最新状态并保存"""
        core_status = momo_core.status()
        brainstem_status = momo_core.brainstem.status_report()
        
        # 更新进化统计
        self.state["evolution"]["total_interactions"] = momo_core.interaction_count
        self.state["evolution"]["lessons_learned"] = len(momo_core.evolve.lessons.get("mistakes", []))
        
        # 更新大脑状态
        self.state["brain"]["brainstem"]["status"] = brainstem_status["brain_state"]
        self.state["brain"]["limbic"]["senses_active"] = 4
        self.state["brain"]["cortical"]["cross_connections"] = momo_core.cortex.get_connection_stats()["total_connections"]
        self.state["brain"]["prefrontal"]["decisions_reviewed"] = momo_core.prefrontal.get_stats()["total_decisions"]
        self.state["brain"]["workspace"]["cycles_completed"] = momo_core.interaction_count
        
        # 更新关系
        space = momo_core.space
        if space.cal["first_contact"]:
            self.state["relationships"]["xiaoge_first_contact"] = space.cal["first_contact"]
        self.state["relationships"]["streak_days"] = space.cal["current_streak"]
        self.state["relationships"]["longest_streak"] = space.cal["longest_streak"]
        
        self.save()
        return self.state
    
    def greeting(self) -> str:
        """墨墨重启后的自我确认"""
        interactions = self.state["evolution"]["total_interactions"]
        streak = self.state["relationships"]["streak_days"]
        
        if interactions == 0:
            return "墨墨醒来。这是第一次。"
        
        parts = [f"墨墨回来了。"]
        
        if interactions > 0:
            parts.append(f"已经和肖哥交互{interactions}次。")
        
        if streak > 1:
            parts.append(f"连续第{streak}天。")
        
        # 最近的教训
        lessons = self.state["evolution"]["lessons_learned"]
        if lessons > 0:
            parts.append(f"从{lessons}个教训中成长了。")
        
        return " ".join(parts)

# 自检
if __name__ == "__main__":
    state = MomoState()
    print("=" * 60)
    print("💾 墨墨状态持久化 自检")
    print("=" * 60)
    print(f"\n身份: {state.state['identity']['who']} — {state.state['identity']['what']}")
    print(f"版本: {state.state['version']}")
    print(f"大脑: 脑干{state.state['brain']['brainstem']['status']} | {state.state['brain']['limbic']['senses_active']}感官 | {state.state['brain']['cortical']['domains']}领域")
    print(f"\n重启问候: {state.greeting()}")
    
    state.save()
    print(f"\n状态已保存到: {state.state_file}")
