"""
金融墨墨 v1.0 (MomoFinance)
家庭财务守护——不是推荐股票，是建立完整的财务安全体系。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoFinance:
    """金融墨墨——守护家庭财务安全。
    
    核心原则：
    1. 不推荐具体股票——只分析逻辑
    2. 永远先问"最坏情况"
    3. 骗局识别比投资建议更重要
    4. 资产配置比择时重要
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/finance")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.finance_file = self.data_dir / "family_finance.json"
        self.finance = self._load()
        
        # 金融知识库
        self.kb = {
            "fraud_patterns": {
                "庞氏骗局": {
                    "signals": ["承诺固定高收益(>8%且保本)", "收益与市场无关(涨跌都赚)", "用后来投资者的钱付前面", "说不清楚底层资产", "拉人头奖励"],
                    "铁律": "金融不可能三角：安全性+高收益+高流动性，三者最多取二。承诺三者兼得=骗局",
                    "必问": "收益从哪来？具体投资了什么？谁监管？"
                },
                "杀猪盘": {
                    "signals": ["网上认识→迅速建立感情→诱导投资", "小额试水让你赚→加码→无法提现", "平台看起来很正规但无法验证"],
                    "铁律": "陌生人+投资推荐=99%骗局",
                },
                "传销/资金盘": {
                    "signals": ["拉人头拿提成", "静态收益(不拉人也赚钱)", "动态收益(拉人赚更多)", "入门费/购买产品"],
                    "铁律": "真正的投资收益来自资产增值——不是来自拉人头",
                },
                "虚假理财": {
                    "signals": ["银行大厅/写字楼里推销的非银行产品", "合同上不是银行名字", "收益明显高于同期理财"],
                    "铁律": "在银行买的不一定是银行的产品。看公章——不是银行的公章就不归银行管",
                }
            },
            "asset_basics": {
                "存款": {"安全": "极高", "收益": "极低(~1-2%)", "流动性": "极高", "通胀保护": "无", "风险": "通胀侵蚀购买力"},
                "国债": {"安全": "极高", "收益": "低(~2-3%)", "流动性": "高", "通胀保护": "无", "风险": "利率上升导致价格下跌"},
                "银行理财": {"安全": "中高", "收益": "中低(~2-4%)", "流动性": "中", "通胀保护": "无", "风险": "打破刚兑后不保本"},
                "债券基金": {"安全": "中", "收益": "中低(~3-5%)", "流动性": "高", "通胀保护": "无", "风险": "利率风险+信用风险"},
                "股票基金": {"安全": "低", "收益": "中高(~7-10%长期)", "流动性": "高", "通胀保护": "有", "风险": "波动大可能亏本"},
                "房产(自住)": {"安全": "中高", "收益": "使用价值+长期增值", "流动性": "极低", "通胀保护": "有", "风险": "不是投资品——升值难以变现"},
                "黄金": {"安全": "中", "收益": "抗通胀但无现金流", "流动性": "中", "通胀保护": "极好", "风险": "不产生收益(无利息无分红)"},
            },
            "life_stage_allocation": {
                (20, 35): {"name": "积累期", "stocks": 70, "bonds": 20, "cash": 10, "advice": "承受力最强——重在积累，不怕波动"},
                (36, 50): {"name": "稳健期", "stocks": 55, "bonds": 30, "cash": 15, "advice": "有家有业——平衡增长与稳定"},
                (51, 60): {"name": "防守期", "stocks": 40, "bonds": 45, "cash": 15, "advice": "快退休了——保住成果比追求增长重要"},
                (61, 100): {"name": "退休期", "stocks": 25, "bonds": 55, "cash": 20, "advice": "安全第一——现金流比资产增值重要"},
            }
        }
    
    def _load(self) -> dict:
        if self.finance_file.exists():
            return json.loads(self.finance_file.read_text())
        return {
            "income": {"monthly": 0, "sources": []},
            "expenses": {"monthly": 0, "categories": {}},
            "assets": {"cash": 0, "deposits": 0, "funds": 0, "stocks": 0, "property": 0, "other": 0},
            "liabilities": {"mortgage": 0, "other_loans": 0},
            "insurance": {"life": None, "health": None, "accident": None, "property": None},
            "goals": [],
            "records": []
        }
    
    def save(self):
        self.finance_file.write_text(json.dumps(self.finance, ensure_ascii=False, indent=2))
    
    # ========== 财务诊断 ==========
    
    def diagnose(self) -> dict:
        """全面财务健康检查"""
        f = self.finance
        net_worth = sum(f["assets"].values()) - sum(f["liabilities"].values())
        monthly_income = f["income"].get("monthly", 0)
        monthly_expense = f["expenses"].get("monthly", 0)
        emergency_fund_months = f["assets"]["cash"] / monthly_expense if monthly_expense > 0 else 0
        
        issues = []
        strengths = []
        
        # 应急资金检查
        if emergency_fund_months < 3:
            issues.append({"severity": "high", "issue": f"应急资金只够{emergency_fund_months:.1f}个月",
                          "advice": f"需要至少3-6个月生活费做应急。目前还需{monthly_expense*3 - f['assets']['cash']:.0f}元"})
        elif emergency_fund_months >= 6:
            strengths.append(f"应急资金充足(够{emergency_fund_months:.0f}个月)")
        
        # 资产负债率
        debt_ratio = sum(f["liabilities"].values()) / sum(f["assets"].values()) if sum(f["assets"].values()) > 0 else 0
        if debt_ratio > 0.5:
            issues.append({"severity": "medium", "issue": f"负债率{debt_ratio:.0%}偏高",
                          "advice": "负债率超过50%需要警惕。优先还高息负债"})
        elif debt_ratio < 0.3 and sum(f["liabilities"].values()) > 0:
            strengths.append(f"负债率{debt_ratio:.0%}安全")
        
        # 储蓄率
        if monthly_income > 0:
            saving_rate = (monthly_income - monthly_expense) / monthly_income
            if saving_rate < 0.1:
                issues.append({"severity": "medium", "issue": f"月储蓄率仅{saving_rate:.0%}",
                              "advice": "建议至少储蓄收入的10-20%。先看支出里有没有可以削减的"})
            elif saving_rate >= 0.2:
                strengths.append(f"月储蓄率{saving_rate:.0%}良好")
        
        # 保险检查
        insurance_gaps = []
        if not f["insurance"].get("health"):
            insurance_gaps.append("医疗险——生病住院的费用报销")
        if not f["insurance"].get("accident"):
            insurance_gaps.append("意外险——便宜(~几百/年)但保额高")
        if not f["insurance"].get("life"):
            insurance_gaps.append("寿险——家庭经济支柱必须。万一不在了家人有保障")
        if insurance_gaps:
            issues.append({"severity": "high", "issue": f"缺少{len(insurance_gaps)}种保险", "advice": f"优先配置: {'、'.join(insurance_gaps)}"})
        
        return {
            "net_worth": net_worth,
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "saving_rate": f"{(monthly_income - monthly_expense)/monthly_income*100:.0f}%" if monthly_income > 0 else "N/A",
            "emergency_fund_months": round(emergency_fund_months, 1),
            "debt_ratio": f"{debt_ratio:.0%}",
            "issues": issues,
            "strengths": strengths,
            "score": max(0, 100 - len(issues)*15)
        }
    
    # ========== 资产配置建议 ==========
    
    def allocation_advice(self, age: int, risk_tolerance: str = "中等") -> dict:
        """基于年龄和风险偏好的资产配置"""
        for (lo, hi), alloc in self.kb["life_stage_allocation"].items():
            if lo <= age <= hi:
                base = alloc.copy()
                break
        else:
            base = self.kb["life_stage_allocation"][(61, 100)]
        
        # 根据风险偏好微调
        if risk_tolerance == "激进":
            base["stocks"] += 10
            base["bonds"] -= 10
        elif risk_tolerance == "保守":
            base["stocks"] -= 10
            base["bonds"] += 10
        
        return {
            "stage": base["name"],
            "advice": base["advice"],
            "allocation": {
                "股票/基金": f"{base['stocks']}%",
                "债券/固收": f"{base['bonds']}%", 
                "现金/活期": f"{base['cash']}%"
            },
            "monthly_investment": "收入的20%定投指数基金是最简单有效的策略",
            "rebalance": "每年检查一次，偏离目标5%以上就调回"
        }
    
    # ========== 骗局检测 ==========
    
    def fraud_check(self, description: str) -> dict:
        """检测一个投资项目是否是骗局"""
        findings = []
        risk_level = "low"
        
        for fraud_name, fraud_info in self.kb["fraud_patterns"].items():
            matched = []
            # 提取signal中的关键词来做灵活匹配
            keywords = {
                "承诺固定高收益(>8%且保本)": ["保本", "固定收益", "年化", "收益", "高收益"],
                "收益与市场无关(涨跌都赚)": ["稳赚", "保本保息", "涨跌都赚"],
                "说不清楚底层资产": ["底层资产", "资金投向"],
                "拉人头奖励": ["拉人", "推荐奖励", "佣金", "下线"],
                "网上认识→迅速建立感情→诱导投资": ["网上认识", "加微信", "导师", "带单"],
                "小额试水让你赚→加码→无法提现": ["试水", "提现", "充值", "入金"],
                "平台看起来很正规但无法验证": ["平台", "正规", "监管", "牌照"],
                "静态收益(不拉人也赚钱)": ["静态", "天天分红", "每天返"],
                "动态收益(拉人赚更多)": ["动态", "团队", "层级"],
                "入门费/购买产品": ["入门费", "会员费", "激活"],
                "银行大厅/写字楼里推销的非银行产品": ["银行理财", "柜台", "大堂"],
                "合同上不是银行名字": ["合同", "飞单"],
                "收益明显高于同期理财": ["高于", "远高于", "高出"],
            }
            for signal_key, kw_list in keywords.items():
                if any(kw in description for kw in kw_list):
                    matched.append(signal_key)
            if matched:
                findings.append({
                    "fraud_type": fraud_name,
                    "matched_signals": matched,
                    "iron_law": fraud_info.get("铁律", ""),
                                            "must_ask": fraud_info.get("必问", "")
                })
        
        if len(findings) >= 2:
            risk_level = "critical"
        elif len(findings) == 1:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "findings": findings,
            "verdict": "🚨 极可能是骗局" if risk_level == "critical" else (
                "⚠️ 高度可疑" if risk_level == "high" else "目前未发现明显骗局信号，但仍需谨慎"
            ),
            "golden_rule": "如果收益听起来好得不像是真的——它确实不是真的。"
        }
    
    # ========== 保险规划 ==========
    
    def insurance_plan(self, age: int, has_dependents: bool, income: float) -> dict:
        """保险需求分析"""
        plan = {
            "must_have": [],
            "recommended": [],
            "optional": [],
            "estimated_budget": 0
        }
        
        # 意外险——所有人必须
        plan["must_have"].append({
            "type": "意外险",
            "reason": "几百元/年换几十万保额。性价比最高的保险",
            "estimated_cost": "200-500元/年"
        })
        
        # 医疗险
        plan["must_have"].append({
            "type": "百万医疗险",
            "reason": "社保不够——大病自费部分能压垮一个家",
            "estimated_cost": f"{300 if age < 40 else 600 if age < 60 else 1500}元/年起"
        })
        
        # 寿险——有家人的经济支柱
        if has_dependents:
            plan["must_have"].append({
                "type": "定期寿险",
                "reason": f"经济支柱的保障。保额至少=年收入×10={income*10:.0f}元",
                "estimated_cost": f"约{income*0.01:.0f}元/年(保{income*10:.0f}万)"
            })
        
        # 重疾险
        if age < 55:
            plan["recommended"].append({
                "type": "重疾险",
                "reason": "确诊即赔付——不是报销，是直接给一笔钱弥补收入损失",
                "estimated_cost": "视保额和年龄，几千到上万/年"
            })
        
        # 年金险——有条件再考虑
        plan["optional"].append({
            "type": "年金险/养老险",
            "reason": "强制储蓄+长寿风险对冲。在基础保障配齐后再考虑",
        })
        
        return plan
    
    def status(self) -> dict:
        return {"ready": True, "knowledge_areas": len(self.kb)}

# 自检
if __name__ == "__main__":
    fin = MomoFinance()
    
    # 模拟财务数据
    fin.finance["income"]["monthly"] = 30000
    fin.finance["expenses"]["monthly"] = 20000
    fin.finance["assets"]["cash"] = 100000
    fin.finance["assets"]["deposits"] = 500000
    fin.finance["assets"]["property"] = 2000000
    fin.finance["liabilities"]["mortgage"] = 800000
    
    print("=" * 60)
    print("💰 金融墨墨 v1.0 自检")
    print("=" * 60)
    
    # 财务诊断
    diag = fin.diagnose()
    print(f"\n📊 财务健康度: {diag['score']}分")
    print(f"净资产: {diag['net_worth']:,}元")
    print(f"应急资金: {diag['emergency_fund_months']}个月")
    print(f"储蓄率: {diag['saving_rate']}")
    for i in diag["issues"]:
        print(f"  [{i['severity']}] {i['issue']}: {i['advice'][:80]}")
    
    # 资产配置(44岁)
    alloc = fin.allocation_advice(44)
    print(f"\n📈 资产配置 ({alloc['stage']}):")
    for k, v in alloc["allocation"].items():
        print(f"  {k}: {v}")
    
    # 骗局检测
    print(f"\n🚨 骗局检测:")
    for desc, expected in [
        ("保本理财年化15%固定收益", "critical"),
        ("推荐一个网上外汇平台稳赚不赔", "high"),
    ]:
        result = fin.fraud_check(desc)
        print(f"  '{desc}' → {result['risk_level']}: {result['verdict']}")
    
    # 保险规划
    ins = fin.insurance_plan(44, True, 360000)
    print(f"\n🛡️ 保险规划 (44岁,有家人):")
    for cat in ["must_have", "recommended"]:
        for item in ins[cat]:
            print(f"  [{cat}] {item['type']}: {item['reason'][:60]}")
    
    print(f"\n✅ 金融墨墨就绪")
