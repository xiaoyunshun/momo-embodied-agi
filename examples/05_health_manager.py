"""
示例 5：健康管理助手（个人健康场景）

模拟墨墨跟踪健康指标、分析体检结果、给出饮食建议。
"""
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from momo.runner import MomoRunner


class HealthAvatar:
    """健康管理分身"""

    def __init__(self):
        self.name = "健康管家"
        self.version = "1.0.0"
        self.knowledge = {
            "转氨酶": {
                "正常范围": "10-40 U/L",
                "偏高原因": "脂肪肝、药物性肝损伤、饮酒、病毒性肝炎",
                "建议": "复查肝功全套+乙肝丙肝+肝脏超声，控制饮食和体重",
            },
            "血压": {
                "正常范围": "收缩压<120 舒张压<80 mmHg",
                "偏高原因": "盐摄入过多、压力、肥胖、缺乏运动",
                "建议": "每日测血压，低盐饮食，每周150分钟有氧运动",
            },
            "血糖": {
                "正常范围": "空腹 3.9-6.1 mmol/L",
                "偏高原因": "胰岛素抵抗、饮食结构不合理",
                "建议": "控制碳水化合物摄入，定期监测糖化血红蛋白",
            },
            "血脂": {
                "正常范围": "总胆固醇<5.2 mmol/L, LDL<3.4 mmol/L",
                "偏高原因": "高脂饮食、缺乏运动、遗传因素",
                "建议": "减少饱和脂肪摄入，增加膳食纤维，规律运动",
            },
            "尿酸": {
                "正常范围": "男性<420 μmol/L",
                "偏高原因": "高嘌呤饮食、饮酒、肾功能减退",
                "建议": "控制海鲜/动物内脏/啤酒摄入，多喝水(>2000ml/天)",
            },
            "体重": {
                "正常范围": "BMI 18.5-23.9",
                "偏高原因": "能量摄入>消耗",
                "建议": "均衡饮食，控制总热量，每周运动3-5次",
            },
        }

    def process(self, text: str) -> dict:
        text_lower = text.lower()
        response_parts = []

        for keyword, info in self.knowledge.items():
            if keyword in text_lower:
                response_parts.append(
                    f"📊 {keyword}\n"
                    f"  正常范围: {info['正常范围']}\n"
                    f"  可能原因: {info['偏高原因']}\n"
                    f"  💡 建议: {info['建议']}"
                )

        if not response_parts:
            return {"response": "", "confidence": 0.0}

        return {
            "response": "🏥 健康分析结果：\n\n" + "\n\n".join(response_parts),
            "confidence": 0.85,
        }

    def help(self) -> dict:
        return {
            "name": self.name,
            "description": "健康指标分析与饮食建议",
            "trackable": list(self.knowledge.keys()),
        }


runner = MomoRunner(xiaoge_name="用户")
runner.register_avatar("health", HealthAvatar())
runner.start()

tests = [
    "最近体检转氨酶偏高怎么办",
    "血压有点高需要注意什么",
    "尿酸高饮食上怎么控制",
]

for test in tests:
    resp = runner.interact(test)
    print(f"\n🩺 问: {test}")
    if resp["response"]:
        print(f"答 [{resp['avatar']}]:")
        print(resp["response"])
    else:
        print(f"ℹ️  未匹配到健康指标")

print("\n✅ 示例 5 完成 —— 健康管理助手")
runner.stop()
