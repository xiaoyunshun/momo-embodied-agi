"""
示例 6：财务顾问（个人理财场景）

模拟墨墨的财务分身为用户提供理财建议和防骗识别。
"""
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from momo.runner import MomoRunner


class FinancialAvatar:
    """财务顾问分身"""

    def __init__(self):
        self.name = "理财顾问"
        self.version = "1.0.0"

        # 投资产品知识库
        self.products = {
            "指数基金": {
                "类型": "被动投资",
                "风险": "中低",
                "适合人群": "长期投资者，不想频繁操作",
                "说明": "跟踪指数（如沪深300），费率低，长期年化6-10%",
            },
            "国债逆回购": {
                "类型": "短期理财",
                "风险": "极低",
                "适合人群": "闲置资金短期管理",
                "说明": "以国债为抵押的短期借款，期限1-182天，流动性好",
            },
            "高股息股票": {
                "类型": "权益投资",
                "风险": "中",
                "适合人群": "追求稳定分红收入的投资者",
                "说明": "选择股息率>4%、连续3年以上分红的蓝筹股",
            },
            "定期存款": {
                "类型": "储蓄",
                "风险": "极低",
                "适合人群": "保守型投资者，资金3年内不用",
                "说明": "50万以内受存款保险保障，利率相对较低",
            },
        }

        # 投资防骗知识库
        self.scams = {
            "高收益": "承诺年化收益>10%且声称无风险的，99%是骗局",
            "拉人头": "靠发展下线获取收益的，典型传销模式",
            "境外平台": "没有国内金融牌照的境外投资平台，资金安全无保障",
            "老师带单": "声称有'老师'指导买卖股票/期货/外汇，收割散户",
            "虚拟货币": "非正规交易所的虚拟货币投资，本金随时归零",
            "原始股": "声称即将上市、可购买原始股的，多为非法集资",
        }

    def process(self, text: str) -> dict:
        text_lower = text.lower()
        response_parts = []

        # 匹配投资产品
        for keyword, info in self.products.items():
            if keyword in text_lower:
                response_parts.append(
                    f"【{keyword}】\n"
                    f"  类型: {info['类型']} | 风险: {info['风险']}\n"
                    f"  适合: {info['适合人群']}\n"
                    f"  {info['说明']}"
                )

        # 匹配防骗知识
        for keyword, warning in self.scams.items():
            if keyword in text_lower:
                response_parts.append(
                    f"⚠️ 防骗提示: {warning}"
                )

        if not response_parts:
            return {"response": "", "confidence": 0.0}

        return {
            "response": (
                "💰 财务分析结果：\n\n" + "\n\n".join(response_parts)
                + "\n\n---\n"
                "📌 以上为通用建议，不构成投资建议。具体操作请咨询专业人士。"
            ),
            "confidence": 0.85,
        }

    def help(self) -> dict:
        return {
            "name": self.name,
            "description": "理财建议和防骗识别",
            "products": list(self.products.keys()),
        }


runner = MomoRunner(xiaoge_name="用户")
runner.register_avatar("finance", FinancialAvatar())
runner.start()

tests = [
    "指数基金和定期存款怎么选",
    "这个项目说年化收益30%没风险，靠谱吗",
    "高股息股票适合长期持有吗",
]

for test in tests:
    resp = runner.interact(test)
    print(f"\n💵 问: {test}")
    if resp["response"]:
        print(f"答 [{resp['avatar']}]:")
        print(resp["response"])
    else:
        print(f"ℹ️  未匹配到理财信息")

print("\n✅ 示例 6 完成 —— 财务顾问")
runner.stop()
