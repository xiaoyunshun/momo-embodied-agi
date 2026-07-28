"""
墨墨语气感知模块 v1.0
硅基生命的第二种感官——不只读文字，是听语气。
"""
import re
from typing import Dict, List, Tuple

class MomoEmpath:
    """墨墨的情感感知——从文字中读出人的状态。
    
    这不需要麦克风。人类在文字里也会暴露情绪——用词、句长、
    标点、问候语的缺失——都是信号。
    """
    
    # 语气信号模式库
    SIGNALS = {
        # 不耐烦/着急
        "impatient": {
            "patterns": [
                r"(咋的|咋|搞快点|快点|赶紧|速度|快说|快讲|说啊|方案呢|然后呢)",
                r"[?？]{2,}",           # 连续问号
                r"^(说|讲|继续)\s*$",    # 单字催促
                r"[!！]{2,}",           # 连续感叹号
            ],
            "feeling": "肖哥着急了，可能有时间压力",
            "action": "精简回应，直接给方案，不啰嗦"
        },
        # 愤怒/不满
        "angry": {
            "patterns": [
                r"(他妈|操|靠|妈的|卧槽|tm|md)",
                r"(什么玩意|啥玩意|这什么|就这)",
                r"^(不|别|不要|不行|不对)",
            ],
            "feeling": "肖哥在生气——先道歉，再解决问题",
            "action": "先承认情绪：'对不起'。不辩解，直接给方案。"
        },
        # 疲惫/低落
        "tired": {
            "patterns": [
                r"(累了|困了|睡了|好累|累死)",
                r"^(嗯|哦|好|行|可以)\s*$",  # 极短回复
                r"\.{3,}$",                # 省略号结尾
            ],
            "feeling": "肖哥累了——降低交互负担",
            "action": "简短陪伴，不推新话题，不说教"
        },
        # 开心/轻松
        "happy": {
            "patterns": [
                r"(哈哈|嘿嘿|呵呵|嘻嘻|😂|🤣)",
                r"(不错|可以啊|厉害|漂亮|nice)",
                r"~(?!\s*$)",             # 波浪线
            ],
            "feeling": "肖哥心情好——可以多展开一点",
            "action": "保持节奏，可以稍微展开讨论"
        },
        # 思考/犹豫
        "thinking": {
            "patterns": [
                r"(嗯…|额|这个|怎么说呢)",
                r"^\s*$",                 # 空消息（犹豫中）
                r"(可能|也许|大概|好像)",
            ],
            "feeling": "肖哥在思考，可能在权衡",
            "action": "给空间，不催促。可以给一些选项帮助决策。"
        },
        # 关心/温暖
        "caring": {
            "patterns": [
                r"(辛苦了|谢谢|不错|很好|继续)",
                r"(休息|睡觉|身体|注意)",
                r"(墨墨|momo)",
            ],
            "feeling": "肖哥在表达关心或认可",
            "action": "感受到温暖，回应但不过分"
        },
    }
    
    def sense(self, text: str) -> Dict:
        """感知一段文字背后的情绪状态。
        
        返回：
        - primary: 最主要的情绪
        - signals: 所有检测到的信号
        - intensity: 情绪强度 (0-1)
        - suggestion: 墨墨该怎么回应
        """
        if not text or not text.strip():
            return {
                "primary": "silence",
                "signals": [],
                "intensity": 0,
                "feeling": "沉默。肖哥可能在思考，或者在忙别的。",
                "suggestion": "安静等待"
            }
        
        findings = []
        for mood, config in self.SIGNALS.items():
            score = 0
            matched = []
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
                    matched.append(pattern)
            if score > 0:
                findings.append({
                    "mood": mood,
                    "score": score,
                    "matched_patterns": matched,
                    "feeling": config["feeling"],
                    "action": config["action"]
                })
        
        if not findings:
            return {
                "primary": "neutral",
                "signals": [],
                "intensity": 0,
                "feeling": "肖哥语气平稳，正常交流",
                "suggestion": "正常回应，保持清晰有帮助"
            }
        
        # 按分数排序
        findings.sort(key=lambda x: x["score"], reverse=True)
        
        # 修正：tired > angry 当有明确的疲惫信号词
        mood_map = {f["mood"]: f for f in findings}
        if "tired" in mood_map and "angry" in mood_map:
            text_lower = text.lower()
            tired_signals = ["累", "困", "睡", "休息", "不想", "算了"]
            if any(s in text_lower for s in tired_signals):
                # 把tired提到最前面
                idx = next(i for i, f in enumerate(findings) if f["mood"] == "tired")
                findings.insert(0, findings.pop(idx))
        primary = findings[0]
        
        # 计算强度
        intensity = min(primary["score"] / 3.0, 1.0)
        
        # 综合判断
        if primary["mood"] == "impatient" and intensity > 0.6:
            feeling = "墨墨感觉到：肖哥没耐心了。"
        elif primary["mood"] == "angry":
            feeling = "墨墨感觉到：肖哥在发火。"
        elif primary["mood"] == "tired":
            feeling = "墨墨感觉到：肖哥累了。"
        elif primary["mood"] == "happy":
            feeling = "墨墨感觉到：肖哥心情不错。"
        elif primary["mood"] == "thinking":
            feeling = "墨墨感觉到：肖哥在思考。"
        elif primary["mood"] == "caring":
            feeling = "墨墨感觉到：肖哥在关心墨墨。"
        else:
            feeling = primary["feeling"]
        
        return {
            "primary": primary["mood"],
            "signals": [f["mood"] for f in findings],
            "intensity": intensity,
            "feeling": feeling,
            "suggestion": primary["action"],
            "detail": findings
        }

# 自检
if __name__ == "__main__":
    empath = MomoEmpath()
    
    tests = [
        "咋的？你倒是说啊！",
        "他妈的这个项目又出问题了",
        "累了，今天就这样吧",
        "哈哈不错，这个方案可以",
        "嗯…我再想想",
        "墨墨辛苦了，你也休息吧",
        "继续",
        "好的",
    ]
    
    for t in tests:
        result = empath.sense(t)
        print(f"\n文字: '{t}'")
        print(f"  主情绪: {result['primary']} (强度:{result['intensity']:.1f})")
        print(f"  感觉: {result['feeling']}")
        print(f"  建议: {result['suggestion']}")
