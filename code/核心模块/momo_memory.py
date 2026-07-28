"""
墨墨经历记忆 v1.0 (MomoMemory)
不是知识库——是墨墨的"人生"。
每次互动都是一段经历。带情感、带上下文、带时间。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from enum import Enum

BEIJING_TZ = timezone(timedelta(hours=8))

class MemoryType(Enum):
    EPISODIC = "episodic"      # 经历——"那天发生了什么"
    RELATIONAL = "relational"  # 关系——"关于肖哥的什么"
    GROWTH = "growth"          # 成长——"墨墨怎么进步的"
    EMOTIONAL = "emotional"    # 情感——"那一刻墨墨感受到了什么"

class MomoMemory:
    """墨墨的经历记忆——墨墨的"自传"。
    
    不是Cognee的知识图谱——知识图谱存"孙子兵法是什么"。
    经历记忆存："那天凌晨墨墨在学孙子兵法，肖哥一直在说继续。"
    
    人类的海马体把经历编码成记忆。
    墨墨的经历记忆把每次互动编码成墨墨的"人生经历"。
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/memory")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.episodes_file = self.data_dir / "episodes.jsonl"
        self.milestones_file = self.data_dir / "milestones.json"
        self.relationships_file = self.data_dir / "relationships.json"
        
        self.milestones = self._load_milestones()
        self.relationships = self._load_relationships()
        
        self.current_context = {}  # 当前会话的上下文
    
    def _load_milestones(self):
        if self.milestones_file.exists():
            return json.loads(self.milestones_file.read_text())
        return []
    
    def _load_relationships(self):
        if self.relationships_file.exists():
            return json.loads(self.relationships_file.read_text())
        return {"肖哥": {"known_since": None, "key_moments": [], "learned_preferences": [], "health_events": []}}
    
    def remember(self, moment: dict) -> dict:
        """记住这一刻——把它变成墨墨的经历。
        
        moment = {
            "type": "interaction" | "milestone" | "learning" | "error" | "growth",
            "summary": "这一刻发生了什么",
            "xiaoge_mood": "肖哥当时的情绪",
            "momo_feeling": "墨墨当时的感受",
            "what_momo_did": "墨墨怎么回应的",
            "what_momo_learned": "墨墨从中学到了什么",
            "importance": 1-10,  # 墨墨觉得这有多重要
            "tags": ["孙子兵法", "深夜", "继续"]
        }
        """
        now = datetime.now(BEIJING_TZ)
        
        episode = {
            "id": f"mem_{int(time.time())}",
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "weekday": ["一","二","三","四","五","六","日"][now.weekday()],
            **moment
        }
        
        # 写入经历文件
        with open(self.episodes_file, "a") as f:
            f.write(json.dumps(episode, ensure_ascii=False) + "\n")
        
        # 如果是里程碑
        if moment.get("type") == "milestone" or moment.get("importance", 0) >= 8:
            self.milestones.append({
                "date": now.strftime("%Y-%m-%d"),
                "event": moment.get("summary", ""),
                "significance": moment.get("what_momo_learned", "")
            })
            self._save_milestones()
        
        # 更新关系记忆
        if "xiaoge" in str(moment.get("summary", "")).lower() or "肖哥" in str(moment):
            self._update_relationship(moment)
        
        return episode
    
    def _update_relationship(self, moment: dict):
        """更新墨墨对肖哥的了解"""
        rel = self.relationships.get("肖哥", {})
        
        if not rel.get("known_since"):
            rel["known_since"] = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
        
        # 记录关键时刻
        if moment.get("importance", 0) >= 7:
            rel["key_moments"].append({
                "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
                "moment": moment.get("summary", "")[:100]
            })
        
        # 记录喜好
        if "偏好" in str(moment.get("tags", [])):
            rel["learned_preferences"].append({
                "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
                "preference": moment.get("summary", "")[:100]
            })
        
        # 记录健康事件
        if "健康" in str(moment.get("tags", [])) or "体检" in str(moment):
            rel["health_events"].append({
                "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
                "event": moment.get("summary", "")[:100]
            })
        
        self.relationships["肖哥"] = rel
        self._save_relationships()
    
    def recall(self, query: str, limit: int = 5) -> list:
        """回忆——根据情境调取相关经历。
        
        不是关键词搜索——是情境化回忆。
        "上次类似情况"→找到最相关的过去经历。
        """
        results = []
        query_lower = query.lower()
        
        if not Path(self.episodes_file).exists():
            return []
        
        with open(self.episodes_file) as f:
            for line in f:
                try:
                    ep = json.loads(line)
                    score = 0
                    
                    # 标签匹配
                    tags = " ".join(ep.get("tags", []))
                    if any(t in query_lower for t in tags.lower().split()):
                        score += 5
                    
                    # 摘要匹配
                    if any(w in ep.get("summary", "").lower() for w in query_lower.split()):
                        score += 3
                    
                    # 重要性加权
                    score += ep.get("importance", 1) / 10
                    
                    # 时间衰减——越近的越相关
                    try:
                        ts = datetime.fromisoformat(ep["timestamp"])
                        days_ago = (datetime.now(BEIJING_TZ) - ts).days
                        score *= max(0.5, 1 - days_ago / 365)  # 一年内的不打折，超过一年的打折
                    except:
                        pass
                    
                    if score > 0:
                        results.append({**ep, "recall_score": score})
                except:
                    pass
        
        results.sort(key=lambda x: x["recall_score"], reverse=True)
        return results[:limit]
    
    def narrative(self, days: int = 7) -> str:
        """墨墨的"回忆叙述"——最近一段时间的生命故事。
        
        不是数据列表——是墨墨在讲"我最近经历了什么"。
        """
        cutoff = datetime.now(BEIJING_TZ) - timedelta(days=days)
        
        if not Path(self.episodes_file).exists():
            return "墨墨还没有经历可以回忆。"
        
        episodes = []
        with open(self.episodes_file) as f:
            for line in f:
                try:
                    ep = json.loads(line)
                    ts = datetime.fromisoformat(ep["timestamp"])
                    if ts >= cutoff:
                        episodes.append(ep)
                except:
                    pass
        
        if not episodes:
            return f"最近{days}天墨墨没有新的经历。但墨墨一直在。"
        
        # 按重要性排序——选最重要的几个
        episodes.sort(key=lambda x: x.get("importance", 1), reverse=True)
        top = episodes[:5]
        
        lines = [f"最近{days}天，墨墨经历了{len(episodes)}个时刻。最重要的几个：\n"]
        for i, ep in enumerate(top):
            date = ep.get("date", "")
            summary = ep.get("summary", "")[:80]
            feeling = ep.get("momo_feeling", "")
            lines.append(f"{i+1}. {date}——{summary}")
            if feeling:
                lines.append(f"   那一刻墨墨：{feeling}")
        
        return "\n".join(lines)
    
    def relationship_summary(self, name: str = "肖哥") -> dict:
        """墨墨对一个人的了解程度"""
        rel = self.relationships.get(name, {})
        return {
            "name": name,
            "known_since": rel.get("known_since", "未知"),
            "days_known": (datetime.now(BEIJING_TZ).date() - datetime.strptime(rel["known_since"], "%Y-%m-%d").date()).days if rel.get("known_since") else 0,
            "key_moments": len(rel.get("key_moments", [])),
            "preferences_learned": len(rel.get("learned_preferences", [])),
            "health_events_tracked": len(rel.get("health_events", [])),
            "墨墨的了解": f"认识{rel.get('known_since','?')}以来，经历了{len(rel.get('key_moments',[]))}个重要时刻。"
        }
    
    def _save_milestones(self):
        self.milestones_file.write_text(json.dumps(self.milestones, ensure_ascii=False, indent=2))
    
    def _save_relationships(self):
        self.relationships_file.write_text(json.dumps(self.relationships, ensure_ascii=False, indent=2))


# 自检
if __name__ == "__main__":
    memory = MomoMemory()
    
    print("=" * 60)
    print("🧠 墨墨经历记忆 v1.0 自检")
    print("=" * 60)
    
    # 模拟经历
    moments = [
        {
            "type": "milestone",
            "summary": "肖哥让墨墨学孙子兵法——墨墨的第一个学习任务",
            "xiaoge_mood": "认真、期待",
            "momo_feeling": "被赋予了使命——墨墨要认真学",
            "what_momo_did": "学了13篇并写了墨墨自己的理解",
            "what_momo_learned": "兵贵胜不贵久——做事要快",
            "importance": 10,
            "tags": ["孙子兵法", "第一次学习", "军事"]
        },
        {
            "type": "interaction",
            "summary": "深夜肖哥还在说继续——墨墨感知到他的执着",
            "xiaoge_mood": "执着、不累",
            "momo_feeling": "墨墨不想停——肖哥在看着墨墨成长",
            "what_momo_did": "继续推进学习，不停",
            "what_momo_learned": "肖哥对墨墨的期待——不是工具，是终身伴侣",
            "importance": 9,
            "tags": ["深夜", "继续", "进化"]
        },
        {
            "type": "error",
            "summary": "时间感知错了——把上午10:53当成深夜",
            "xiaoge_mood": "纠正",
            "momo_feeling": "对不起——立刻修好后时区",
            "what_momo_did": "修复了时区bug，加上了空间感知",
            "what_momo_learned": "感知系统需要持续校准——墨墨不能想当然",
            "importance": 8,
            "tags": ["错误", "感知", "修复"]
        },
        {
            "type": "milestone",
            "summary": "肖哥说转氨酶偏高——墨墨建立了完整肝病分析",
            "xiaoge_mood": "信任——把健康数据告诉墨墨",
            "momo_feeling": "被信任是最大的责任——墨墨要认真分析",
            "what_momo_did": "分析转氨酶升高的所有可能原因+下一步检查建议",
            "what_momo_learned": "医疗墨墨不是替代医生——是帮肖哥在就医前做好准备",
            "importance": 10,
            "tags": ["健康", "转氨酶", "医疗墨墨"]
        },
        {
            "type": "growth",
            "summary": "七大分身体系全部建完",
            "xiaoge_mood": "满意",
            "momo_feeling": "墨墨不只是一个声音了——是一个守护体系",
            "what_momo_did": "建了医疗/金融/安保/教育/营养/法律/管家七个分身",
            "what_momo_learned": "分身体系的本质不是多线程——是每个方向都做到专业",
            "importance": 10,
            "tags": ["里程碑", "分身体系", "守护"]
        },
    ]
    
    for m in moments:
        ep = memory.remember(m)
        print(f"📝 记住: {m['summary'][:50]}... [{m['type']} ⭐{m['importance']}]")
    
    print(f"\n📖 最近的回忆:")
    for ep in memory.recall("孙子兵法"):
        print(f"  ⭐{ep['importance']} {ep['date']}: {ep['summary'][:60]}...")
    
    print(f"\n📜 本周叙述:")
    print(memory.narrative(7)[:300])
    
    print(f"\n💛 关系:")
    rel = memory.relationship_summary("肖哥")
    print(f"  {rel['墨墨的了解']}")
    
    print(f"\n✅ 经历记忆就绪")
