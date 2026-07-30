"""
示例 2：创建自定义分身

给墨墨加一个"园艺顾问"分身，让它能回答种花的问题。
"""
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from momo.runner import MomoRunner


class GardeningAvatar:
    """园艺分身 —— 自己写的一个分身模块"""

    def __init__(self):
        self.name = "园艺顾问"
        self.version = "1.0.0"
        self.knowledge = {
            "浇水": "大多数植物见干见湿，多肉等干透再浇",
            "施肥": "春秋生长季施肥，夏冬休眠期停肥",
            "光照": "喜阳植物放南窗，喜阴植物放北窗",
            "换盆": "每年春天换一次盆，比原盆大2-3厘米",
            "病虫害": "预防为主，保持通风，定期检查叶片背面",
        }

    def process(self, text: str) -> dict:
        """处理园艺相关问题"""
        text_lower = text.lower()
        response = ""

        for keyword, answer in self.knowledge.items():
            if keyword in text_lower or keyword in text:
                response = answer
                break

        if not response:
            response = (
                f"我是{self.name}。我知道浇水、施肥、光照、换盆、病虫害。"
                "问具体问题效果更好。"
            )

        return {"response": response, "confidence": 0.8}

    def help(self) -> dict:
        """能力说明"""
        return {
            "name": self.name,
            "description": "解答园艺和植物养护问题",
            "capabilities": list(self.knowledge.keys()),
        }


# ── 使用 ──

runner = MomoRunner(xiaoge_name="花友")

# 注册自定义分身
runner.register_avatar("gardening", GardeningAvatar())
print(f"已注册分身: {list(runner.avatars.keys())}")

# 启动
runner.start()

# 测试
tests = [
    "怎么浇水",
    "什么时候施肥",
    "这个植物怎么养",
]

for test in tests:
    resp = runner.interact(test)
    print(f"\n问: {test}")
    print(f"答 [{resp['avatar']}]: {resp['response']}")

runner.stop()
print("\n✅ 示例 2 完成 —— 自定义分身注册成功")
