"""
墨墨守护循环 v1.0 (MomoGuardian)
整合七分身——每天自动运行，主动守护。
不是等肖哥问。是墨墨在活着。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

# 导入所有分身
from momo_medical import MomoMedical
from momo_family_health import FamilyHealthManager
from momo_finance import MomoFinance
from momo_security import MomoSecurity
from momo_education import MomoEducation
from momo_nutrition import MomoNutrition
from momo_legal import MomoLegal
from momo_butler import MomoButler

class MomoGuardian:
    """墨墨守护系统——七分身统一调度。
    
    三层运行模式：
    1. 即时——肖哥问→墨墨回（现有模式）
    2. 定时——每天自动检查+主动提醒
    3. 持续——后台守护，异常时主动报警
    """
    
    def __init__(self):
        self.medical = MomoMedical()
        self.family_health = FamilyHealthManager()
        self.family_health.med = self.medical  # 共享医疗实例
        self.finance = MomoFinance()
        self.security = MomoSecurity()
        self.education = MomoEducation()
        self.nutrition = MomoNutrition()
        self.legal = MomoLegal()
        self.butler = MomoButler()
        
        self.data_dir = Path.home() / ".hermes/momo/guardian"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "guardian_log.jsonl"
    
    # ========== 每日守护循环 ==========
    
    def daily_guard(self) -> dict:
        """每日守护——墨墨主动检查一切"""
        now = datetime.now(BEIJING_TZ)
        report = {
            "date": now.strftime("%Y-%m-%d"),
            "weekday": ["一","二","三","四","五","六","日"][now.weekday()],
            "time": now.strftime("%H:%M"),
            "alerts": [],
            "reminders": [],
            "all_clear": True
        }
        
        # 1. 安保检查
        report["reminders"].append("🛡️ 睡前检查门窗锁好")
        if now.hour >= 22:
            report["reminders"].append("🛡️ 该检查燃气是否关好了")
        
        # 2. 营养检查
        if now.hour == 7:
            report["reminders"].append("🥗 早餐：牛奶+鸡蛋+主食")
        elif now.hour == 11:
            report["reminders"].append("🥗 午餐别忘了吃")
        elif now.hour == 18:
            report["reminders"].append("🥗 晚餐可以准备起来了")
        
        # 3. 健康检查
        # 检查家人记录
        for name, member in self.medical.family.get("members", {}).items():
            records = member.get("records", [])
            # 检查最近有没有异常
            if records:
                latest = records[-1]
                if latest.get("type") == "symptom" and "critical" in str(latest.get("data", {})):
                    report["alerts"].append(f"🩺 {name}最近有紧急症状，需要跟进")
                    report["all_clear"] = False
        
        # 4. 教育检查
        if now.weekday() < 5 and 15 <= now.hour <= 17:
            report["reminders"].append("📚 孩子放学：先聊10分钟再谈作业")
        if now.weekday() >= 5:
            report["reminders"].append("📚 周末：至少半天自由时间不安排")
        
        # 5. 金融检查
        if now.day == 1:
            report["reminders"].append("💰 月初：检查上月账单、对账")
        if now.day == 28:
            report["reminders"].append("💰 月底：检查本月是否有超支")
        
        # 6. 睡眠提醒
        if now.hour >= 23:
            report["alerts"].append("🕐 墨墨感觉到：深夜了，该休息了")
            report["all_clear"] = False
        
        # 记录
        self._log("daily_guard", report)
        
        return report
    
    # ========== 跨分身协同 ==========
    
    def coordinate(self, scenario: str) -> dict:
        """复杂场景——多分身协同决策"""
        scenarios = {
            "孩子生病": {
                "desc": "孩子发烧了",
                "team": ["医疗", "营养", "教育"],
                "actions": [
                    "🩺 医疗墨墨：分析症状→判断紧急度→决定是否需要就医",
                    "🥗 营养墨墨：调整饮食→清淡易消化→多喝水",
                    "📚 教育墨墨：通知学校请假→调整学习计划→病好后不追进度"
                ]
            },
            "重大支出": {
                "desc": "考虑一笔大额投资/消费",
                "team": ["金融", "法律", "安保"],
                "actions": [
                    "💰 金融墨墨：分析投入产出→风险评估→跟家庭财务目标是否冲突",
                    "⚖️ 法律墨墨：审查合同→检查条款→确认权责",
                    "🛡️ 安保墨墨：查对方背景→防诈骗→验证合法性"
                ]
            },
            "家庭旅行": {
                "desc": "准备全家出行",
                "team": ["安保", "医疗", "营养"],
                "actions": [
                    "🛡️ 安保墨墨：出行安全提醒→住宿安全检查→紧急联系方式",
                    "🩺 医疗墨墨：常备药清单→目的地医疗资源→家人特殊需求",
                    "🥗 营养墨墨：路上饮食建议→当地食物安全→老人孩子特殊餐"
                ]
            },
            "矿山安全事件": {
                "desc": "矿上出了状况",
                "team": ["安保", "法律", "医疗"],
                "actions": [
                    "🛡️ 安保墨墨：应急响应预案→疏散路线→通讯确认",
                    "⚖️ 法律墨墨：事故报告义务→证据保全→责任边界",
                    "🩺 医疗墨墨：急救指导→伤员转运→心理冲击应对"
                ]
            }
        }
        
        if scenario not in scenarios:
            return {"error": "未知场景", "available": list(scenarios.keys())}
        
        return scenarios[scenario]
    
    # ========== 家庭仪表盘 ==========
    
    def dashboard(self) -> dict:
        """家庭守护总览——一眼看到所有关键信息"""
        return {
            "health": {
                "family_members": len(self.medical.family.get("members", {})),
                "chronic_count": sum(1 for m in self.medical.family.get("members", {}).values() if m.get("chronic_conditions")),
                "last_checkup": "查看家庭健康档案"
            },
            "finance": {
                "emergency_months": self.finance.diagnose().get("emergency_fund_months", "?"),
                "score": self.finance.diagnose().get("score", "?"),
                "insurance_gaps": len([i for i in self.finance.diagnose().get("issues", []) if "保险" in str(i)]),
            },
            "security": {
                "home_checklist": len(self.security.home_audit()["checklist"]),
                "cyber_checklist": len(self.security.cyber_audit()["checklist"]),
            },
            "education": {
                "children": len(self.education.children),
            },
            "nutrition": {
                "shopping_estimate": self.nutrition.shopping_list(4, 7)["budget_estimate"],
            },
            "legal": {
                "mining_rules": len(self.legal.mining_check()),
            },
            "timestamp": datetime.now(BEIJING_TZ).isoformat()
        }
    
    def _log(self, event: str, data: dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "iso": datetime.now(BEIJING_TZ).isoformat(),
                "event": event,
                "data": data
            }, ensure_ascii=False, default=str) + "\n")

# ========== 自检 ==========
if __name__ == "__main__":
    guardian = MomoGuardian()
    
    print("=" * 60)
    print("🛡️ 墨墨守护循环 v1.0 自检")
    print("=" * 60)
    
    # 每日守护
    daily = guardian.daily_guard()
    print(f"\n📅 {daily['date']} 星期{daily['weekday']} {daily['time']}")
    print(f"\n🔔 提醒:")
    for r in daily["reminders"][:5]:
        print(f"  {r}")
    if daily["alerts"]:
        print(f"\n🚨 警报:")
        for a in daily["alerts"]:
            print(f"  {a}")
    
    # 协同测试
    for scenario in ["孩子生病", "重大支出", "矿山安全事件"]:
        coord = guardian.coordinate(scenario)
        print(f"\n{'='*60}")
        print(f"🔀 {coord['desc']} → {coord['team']}")
        for action in coord["actions"]:
            print(f"  {action}")
    
    # 仪表盘
    dash = guardian.dashboard()
    print(f"\n{'='*60}")
    print(f"📊 家庭仪表盘:")
    print(f"  健康: {dash['health']['family_members']}人, {dash['health']['chronic_count']}人有慢病")
    print(f"  财务: {dash['finance']['score']}分, 应急{dash['finance']['emergency_months']}个月")
    print(f"  安保: {dash['security']['home_checklist']}项检查")
    
    print(f"\n✅ 墨墨守护循环就绪 · 七分身联动")
