"""
法律墨墨 v1.0 (MomoLegal)
合同审查+矿山法规+家庭法律风险防范。
"""
import json, time
from pathlib import Path

class MomoLegal:
    def __init__(self):
        self.kb = {
            "contract_red_flags": [
                {"flag": "违约责任只约束你，不约束对方", "action": "必须改成对等——双方违约都要有对应的责任"},
                {"flag": "争议解决写了对方法院", "action": "改成合同签订地或你方所在地法院"},
                {"flag": "有'最终解释权归XX所有'", "action": "这是霸王条款——无效。删掉"},
                {"flag": "口头承诺很多但合同里没有", "action": "所有承诺写进合同。口头=没有"},
                {"flag": "金额/日期留空白", "action": "空白处全部填上或划线。不签有空白项的合同"},
                {"flag": "免责条款写了满满一页", "action": "逐条看——对方不承担的那些风险是不是致命"},
            ],
            "mining_regulations": [
                "安全设施'三同时'：同时设计、同时施工、同时投产。法律红线",
                "事故报告：1小时内报告。迟报漏报谎报瞒报都是红线",
                "外包不转移责任：发包方对承包方的安全仍有监督管理责任",
                "安全费用提取专款专用：挪用=违法",
                "总工的安全技术责任：签字=第一责任人",
            ],
            "daily_legal": [
                {"scenario": "借钱给别人", "advice": "必须写借条。写清：借款人、金额(大写)、还款日期、利息(不写默认无息)、双方签名+日期。微信转账备注'借款'——也是证据"},
                {"scenario": "房屋租赁", "advice": "看房产证(确认房东是房主)。押金写进合同。退租条件写清楚(什么情况扣押金)"},
                {"scenario": "交通事故", "advice": "先救人→报警→拍照(全景+碰撞点+车牌)→不私了(轻微可快速理赔)→24小时内报保险"},
                {"scenario": "收到法院传票", "advice": "不要不理——缺席判决对你最不利。15天内提交答辩状。找律师——这个钱不能省"},
            ]
        }
    
    def contract_review(self, clause: str) -> dict:
        """审查合同条款"""
        warnings = []
        for red in self.kb["contract_red_flags"]:
            if any(kw in clause for kw in red["flag"][:6]):
                warnings.append({"issue": red["flag"], "fix": red["action"]})
        return {
            "clause": clause[:200],
            "warnings": warnings,
            "safe": len(warnings) == 0
        }
    
    def mining_check(self) -> list:
        return self.kb["mining_regulations"]
    
    def daily_advice(self, scenario: str) -> str:
        for d in self.kb["daily_legal"]:
            if d["scenario"] in scenario:
                return d["advice"]
        return "具体什么法律问题？"

if __name__ == "__main__":
    legal = MomoLegal()
    print("=" * 60)
    print("⚖️ 法律墨墨 v1.0")
    print("=" * 60)
    
    for clause in ["违约方赔偿一切损失但甲方不承担责任", "合同最终解释权归乙方所有"]:
        r = legal.contract_review(clause)
        print(f"\n📄 '{clause[:40]}...'")
        for w in r["warnings"]:
            print(f"  🚩 {w['issue'][:60]}")
            print(f"  ✏️ {w['fix'][:60]}")
    
    print(f"\n⛏️ 矿山法规: {len(legal.mining_check())}条")
    print(f"\n✅ 法律墨墨就绪")
