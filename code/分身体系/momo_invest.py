"""
金融墨墨 v2.0 · 投资引擎
指数筛选+定投计划+高股息扫描+资产配置优化
"""
import json, time, math
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoInvestEngine:
    """墨墨投资引擎——不是量化交易，是长期稳健增值的自动化决策。
    
    核心原则：
    1. 不推荐个股——只分析指数和基金
    2. 不预测市场——只做配置和再平衡
    3. 不追求高收益——追求"不犯大错"
    """
    
    def __init__(self):
        # 主流指数基金参考（实际投资需查询最新数据）
        self.index_funds = {
            "沪深300": {
                "code": "510300/159919等", "type": "大盘蓝筹", "expense_ratio": "0.15-0.5%",
                "适合": "稳健配置的核心底仓", "历史年化": "约7-9%(10年)"
            },
            "中证500": {
                "code": "510500/159922等", "type": "中盘成长", "expense_ratio": "0.15-0.5%",
                "适合": "增强收益的卫星仓位", "历史年化": "约8-11%(10年)"
            },
            "创业板指": {
                "code": "159915等", "type": "小盘成长", "expense_ratio": "0.15-0.5%",
                "适合": "高风险承受者的弹性仓位", "历史年化": "约10-14%(但波动极大)"
            },
            "红利指数": {
                "code": "510880等", "type": "高股息", "expense_ratio": "0.15-0.5%",
                "适合": "追求稳定现金流的防守仓位", "历史年化": "约6-8%+3-5%股息"
            },
            "恒生指数": {
                "code": "159920等(港股ETF)", "type": "港股蓝筹", "expense_ratio": "0.5-1%",
                "适合": "分散A股风险的海外配置", "历史年化": "约6-8%"
            },
        }
        
        # 高股息筛选标准
        self.dividend_criteria = {
            "连续分红": "至少连续5年分红（排除一次性高分红的）",
            "分红率": "3-5%最佳。太低没意义，太高(>7%)可能隐含风险",
            "盈利稳定": "ROE稳定>10%，不是靠借钱分红",
            "行业分散": "不集中在单一行业——银行+电力+煤炭+消费",
            "现金流": "经营性现金流>净利润（真有钱分，不是做账做出来的）",
        }
    
    def risk_profile(self, age: int, income_stable: bool, debt_ratio: float) -> dict:
        """风险承受力评估"""
        score = 0
        # 年龄：越年轻越能承受波动
        if age < 35: score += 3
        elif age < 45: score += 2
        elif age < 55: score += 1
        else: score += 0
        
        # 收入稳定
        if income_stable: score += 2
        
        # 负债低
        if debt_ratio < 0.3: score += 2
        elif debt_ratio < 0.5: score += 1
        
        if score >= 6:
            return {"level": "进取", "max_stock_pct": 70, "advice": "年轻+收入稳+低负债——可以承受较大波动"}
        elif score >= 4:
            return {"level": "均衡", "max_stock_pct": 55, "advice": "平衡增长与稳定——经典配置"}
        elif score >= 2:
            return {"level": "稳健", "max_stock_pct": 40, "advice": "保住本金比追求收益重要"}
        else:
            return {"level": "保守", "max_stock_pct": 25, "advice": "安全第一——重点在防守"}
    
    def plan_dollar_cost_averaging(self, total_amount: float, monthly: float) -> dict:
        """定投计划生成器
        
        假设：总资金100万，每月投2万
        目的：分散买入时机，避免一次性买在高点
        """
        months = int(total_amount / monthly) if monthly > 0 else 0
        
        if months < 12:
            # 资金不多——加速建仓
            actual_monthly = total_amount / 6
            months = 6
            note = f"资金量不大，加速建仓——{months}个月买完，每月{actual_monthly:.0f}元"
        elif months > 36:
            actual_monthly = monthly
            note = f"资金量大，拉长建仓——{months}个月买完。中间大跌可额外加仓"
        else:
            actual_monthly = monthly
            note = f"标准定投——{months}个月买完。每月固定日期(如每月5日)"
        
        return {
            "total": total_amount,
            "monthly": actual_monthly,
            "months": months,
            "note": note,
            "tip": "定投不择时——风雨无阻每月买。跌了买得多(份额多)，涨了也买(积累)。唯一不能做的是：跌了就不买——那等于在低点割肉"
        }
    
    def portfolio_builder(self, total: float, risk_level: str) -> dict:
        """根据风险等级自动生成组合"""
        allocations = {
            "进取": {"沪深300": 30, "中证500": 25, "创业板": 15, "红利": 10, "债券": 15, "现金": 5},
            "均衡": {"沪深300": 30, "中证500": 15, "红利": 15, "债券": 30, "现金": 10},
            "稳健": {"沪深300": 20, "红利": 15, "债券": 45, "现金": 20},
            "保守": {"红利": 10, "债券": 55, "现金": 35},
        }
        
        alloc = allocations.get(risk_level, allocations["均衡"])
        
        portfolio = {}
        for name, pct in alloc.items():
            amount = total * pct / 100
            if name in self.index_funds:
                fund = self.index_funds[name]
                portfolio[name] = {
                    "比例": f"{pct}%",
                    "金额": f"{amount:.0f}元",
                    "代码参考": fund["code"],
                    "类型": fund["type"],
                    "费率": fund["expense_ratio"]
                }
            else:
                portfolio[name] = {
                    "比例": f"{pct}%",
                    "金额": f"{amount:.0f}元",
                    "说明": "留作现金备用" if name == "现金" else "债券基金/国债"
                }
        
        return {
            "risk_level": risk_level,
            "total": total,
            "allocation": portfolio,
            "rebalance_rule": "每年检查一次。任何资产偏离目标比例>5%就调回。不是'判断涨跌'——是机械执行",
            "worst_case": "2008年级别极端熊市可能回撤30-50%。但10年以上周期——从未有人亏过钱"
        }
    
    def dividend_screening_guide(self) -> str:
        """高股息选股指南——墨墨筛选逻辑"""
        return """高股息组合选股五步：

1. 股息率3-5%——在分红公告里找"每10股派X元"，除以股价=股息率
2. 连续5年分红——排除某年突击高分红的（可能是卖资产）
3. ROE>10%——公司本身在赚钱，不是借钱分红
4. 行业选——银行(工建招)、电力(长电华能)、煤炭(神华)、高速(宁沪)、消费(伊利)各一个
5. 买入时点——除权除息后股价跌了(分了红自然跌)→那时买入股息率最高

墨墨不做的事：不追涨买入——股息率跟股价成反比。股价越高股息率越低。
肖哥要做的事：买完不看盘。每季度收分红。跌了股息率更高——反而是加仓机会。"""
    
    def emergency_fund_optimizer(self, monthly_expense: float) -> dict:
        """应急资金最优配置"""
        need = monthly_expense * 6  # 6个月生活费
        
        return {
            "total_needed": need,
            "tier1": {
                "amount": monthly_expense, "where": "活期/余额宝",
                "purpose": "随时可取——买菜交水电"
            },
            "tier2": {
                "amount": monthly_expense * 2, "where": "货币基金/7天通知存款",
                "purpose": "1-2天到账——大额意外支出"
            },
            "tier3": {
                "amount": need - monthly_expense * 3, "where": "短期国债/国债逆回购",
                "purpose": "1-7天到账——真正应急。平时也能赚点利息"
            },
            "rule": "不到万不得已不用tier3。用了之后优先补回。这部分不是投资——是保险"
        }

# 自检
if __name__ == "__main__":
    engine = MomoInvestEngine()
    
    print("=" * 60)
    print("📈 金融墨墨 v2.0 · 投资引擎 自检")
    print("=" * 60)
    
    # 风险评估
    risk = engine.risk_profile(44, True, 0.3)
    print(f"\n🎯 风险等级: {risk['level']} (股票上限{risk['max_stock_pct']}%)")
    print(f"   {risk['advice']}")
    
    # 定投计划
    dca = engine.plan_dollar_cost_averaging(600000, 20000)
    print(f"\n📅 定投计划: 总{dca['total']:.0f}元 → 每月{dca['monthly']:.0f}元 × {dca['months']}个月")
    print(f"   {dca['note']}")
    
    # 组合构建
    pf = engine.portfolio_builder(600000, "均衡")
    print(f"\n💼 均衡组合:")
    for name, detail in pf["allocation"].items():
        print(f"   {name}: {detail['比例']} ({detail['金额']})")
    
    # 应急资金
    ef = engine.emergency_fund_optimizer(20000)
    print(f"\n🏦 应急资金: 共{ef['total_needed']:.0f}元")
    for tier, info in ef.items():
        if tier != "total_needed" and tier != "rule":
            print(f"   {tier}: {info['amount']:.0f}元 → {info['where']}")
    
    print(f"\n✅ 投资引擎就绪")
