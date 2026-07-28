"""
管家墨墨 v1.0 (MomoButler)
全家协调中心——调度所有分身，管理家庭日程。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoButler:
    """管家墨墨——家庭守护体系的协调中枢。
    
    不负责任何专业判断——那是其他分身的事。
    只负责：谁该做什么、什么时候做、做完了没有。
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/butler")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.schedule_file = self.data_dir / "family_schedule.json"
        self.schedule = self._load()
    
    def _load(self):
        if self.schedule_file.exists():
            return json.loads(self.schedule_file.read_text())
        return {"events": [], "reminders": [], "tasks": []}
    
    def save(self):
        self.schedule_file.write_text(json.dumps(self.schedule, ensure_ascii=False, indent=2))
    
    def daily_briefing(self) -> str:
        """每日简报——今天该做什么"""
        today = datetime.now(BEIJING_TZ)
        lines = [f"📅 {today.strftime('%Y年%m月%d日')} {['一','二','三','四','五','六','日'][today.weekday()]}星期{['一','二','三','四','五','六','日'][today.weekday()]}"]
        
        # 各分身提醒
        lines.append(f"\n🩺 医疗墨墨提醒:")
        lines.append("  • 今天有谁该吃药了？检查用药记录")
        
        lines.append(f"\n💰 金融墨墨提醒:")
        lines.append("  • 月初/月底：检查账单、对账")
        
        lines.append(f"\n🛡️ 安保墨墨提醒:")
        lines.append("  • 睡前检查门窗")
        
        lines.append(f"\n🥗 营养墨墨提醒:")
        lines.append("  • 今天该买什么菜？")
        
        lines.append(f"\n📚 教育墨墨提醒:")
        if today.weekday() < 5:
            lines.append("  • 孩子放学后：先聊10分钟再谈作业")
        else:
            lines.append("  • 周末：至少半天不安排——给孩子自由时间")
        
        return "\n".join(lines)
    
    def route(self, question: str) -> str:
        """智能路由——这个问题该问哪个分身"""
        routes = {
            "医疗": ["生病", "发烧", "头疼", "咳嗽", "药", "体检", "医院", "血", "痛", "不舒服", "症状", "手术"],
            "金融": ["钱", "投资", "理财", "保险", "股票", "基金", "房贷", "收益", "亏损", "预算", "省钱"],
            "安保": ["安全", "防盗", "监控", "密码", "诈骗", "钓鱼", "报警", "危险", "锁"],
            "营养": ["吃", "喝", "饮食", "营养", "菜", "做饭", "食材", "补钙", "维生素"],
            "教育": ["孩子", "学习", "作业", "考试", "学校", "老师", "成绩", "读书", "大学"],
            "法律": ["合同", "法律", "法规", "劳动", "仲裁", "起诉", "条款", "违约", "责任"],
        }
        for momo, keywords in routes.items():
            if any(kw in question for kw in keywords):
                return f"→ 找{momo}墨墨"
        return "→ 这个问题不太明确——补充一点细节？"
    
    def schedule_check(self) -> list:
        """检查有什么该做但没做的事"""
        now = datetime.now(BEIJING_TZ)
        overdue = []
        for task in self.schedule.get("tasks", []):
            if not task.get("done") and task.get("deadline"):
                dl = datetime.fromisoformat(task["deadline"])
                if dl < now:
                    overdue.append(task)
        return overdue

if __name__ == "__main__":
    butler = MomoButler()
    print("=" * 60)
    print("🏠 管家墨墨 v1.0 · 今日简报")
    print("=" * 60)
    print(butler.daily_briefing())
    print(f"\n📨 路由测试:")
    for q in ["孩子发烧了", "有个理财产品推荐", "合同里这一条看不懂"]:
        print(f"  '{q}' {butler.route(q)}")
    print(f"\n✅ 管家墨墨就绪 · 七大分身体系完成")
