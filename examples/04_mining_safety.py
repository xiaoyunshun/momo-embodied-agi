"""
示例 4：矿山安全风险分析（行业实战）

模拟墨墨在矿山安全场景中的应用——分析安全隐患并生成管控措施。
"""
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from momo.runner import MomoRunner


class MiningSafetyAvatar:
    """矿山安全分身"""

    def __init__(self):
        self.name = "矿山安全顾问"
        self.version = "1.0.0"
        self.regulations = {
            "通风": {
                "标准": "GB 16423-2020 第5.3条",
                "要求": "井下风速不低于0.15m/s，主通风机连续运转",
            },
            "排水": {
                "标准": "GB 16423-2020 第5.4条",
                "要求": "排水能力不小于最大涌水量的1.2倍",
            },
            "顶板": {
                "标准": "GB 16423-2020 第5.2条",
                "要求": "采掘工作面必须进行顶板监测，空顶距不超过规定",
            },
            "爆破": {
                "标准": "GB 6722-2014",
                "要求": "爆破作业必须严格执行爆破说明书，警戒距离不小于200m",
            },
            "运输": {
                "标准": "GB 16423-2020 第5.5条",
                "要求": "斜坡道运输必须设置防跑车装置，行人不行车",
            },
            "尾矿库": {
                "标准": "GB 50863-2013",
                "要求": "尾矿库必须在线监测，干滩长度不小于70%",
            },
        }

    def process(self, text: str) -> dict:
        """分析矿山安全隐患"""
        text_lower = text.lower()
        response_parts = []

        for keyword, info in self.regulations.items():
            if keyword in text_lower:
                response_parts.append(
                    f"【{keyword}】\n"
                    f"  适用标准: {info['标准']}\n"
                    f"  管控要求: {info['要求']}"
                )

        if not response_parts:
            return {"response": "", "confidence": 0.0}

        return {
            "response": (
                "🧑‍🏭 矿山安全分析结果：\n\n"
                + "\n\n".join(response_parts)
                + "\n\n---\n"
                "⚠️ 以上为系统自动匹配的法规条款，实际应用需结合现场具体条件。"
            ),
            "confidence": 0.85,
        }

    def help(self) -> dict:
        return {
            "name": self.name,
            "description": "分析与矿山安全相关的问题，匹配法规条款",
            "keywords": list(self.regulations.keys()),
        }


# ── 使用 ──

runner = MomoRunner(xiaoge_name="肖工")
runner.register_avatar("mining_safety", MiningSafetyAvatar())
runner.start()

tests = [
    "井下通风系统如何管理",
    "尾矿库有什么安全要求",
    "这个矿的顶板怎么支护",
]

for test in tests:
    resp = runner.interact(test)
    print(f"\n👷 问: {test}")
    if resp["response"]:
        print(f"📋 答 [{resp['avatar']}]:")
        print(resp["response"])
    else:
        print(f"ℹ️  未匹配到相关法规")

print("\n✅ 示例 4 完成 —— 矿山安全风险分析")
runner.stop()
