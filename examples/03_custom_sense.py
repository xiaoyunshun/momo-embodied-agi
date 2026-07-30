"""
示例 3：自定义感官 + 交互循环

给墨墨加一个"天气感官"，让它能感知天气信息并给出建议。
"""
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from momo.runner import MomoRunner


class WeatherSense:
    """天气感官 —— 从文本中提取天气信息"""

    def process(self, text: str) -> dict:
        """从输入中提取天气相关信号"""
        text_lower = text.lower()
        weather_words = {
            "晴": "sunny",
            "雨": "rainy",
            "雪": "snowy",
            "阴": "cloudy",
            "风": "windy",
            "热": "hot",
            "冷": "cold",
            "暖": "warm",
            "凉": "cool",
        }

        detected = []
        for cn, en in weather_words.items():
            if cn in text_lower or en in text_lower:
                detected.append(en)

        return {
            "type": "weather",
            "detected_weather": detected,
            "has_weather_context": len(detected) > 0,
            "summary": f"检测到天气关键词: {', '.join(detected)}" if detected else "无天气信息",
        }


class WeatherAvatar:
    """天气分身 —— 根据天气给出建议"""

    def process(self, text: str) -> dict:
        text_lower = text.lower()
        tips = []

        if any(w in text_lower for w in ["雨", "rainy", "下雨"]):
            tips.append("🌧️ 带伞，路面湿滑注意脚下")
        if any(w in text_lower for w in ["雪", "snowy", "下雪"]):
            tips.append("❄️ 注意保暖，路面结冰小心滑倒")
        if any(w in text_lower for w in ["热", "hot", "高温"]):
            tips.append("🥵 多喝水，避免长时间暴晒")
        if any(w in text_lower for w in ["冷", "cold", "降温"]):
            tips.append("🥶 加件外套，注意别着凉")
        if any(w in text_lower for w in ["风", "windy"]):
            tips.append("💨 风大，高空物品注意固定")

        if tips:
            return {"response": "\n".join(tips), "confidence": 0.9}
        return {"response": "", "confidence": 0.0}


# ── 使用 ──

runner = MomoRunner(xiaoge_name="用户")

# 注册自定义感官
runner.register_sense("weather", WeatherSense())

# 注册天气分身
runner.register_avatar("weather", WeatherAvatar())

runner.start()
print("🧠 墨墨已启动，输入天气相关关键词试试\n")

tests = [
    "今天下雨了",
    "好冷啊",
    "外面风好大",
]

for test in tests:
    resp = runner.interact(test)
    print(f"问: {test}")
    print(f"感知: {resp['perception']['senses']['weather']['summary']}")
    if resp["response"]:
        print(f"答 [{resp['avatar']}]:\n{resp['response']}")
    else:
        print(f"答: (无匹配)")
    print()

runner.stop()
print("✅ 示例 3 完成")
