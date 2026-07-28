"""
墨墨听觉感知 v1.0 (MomoHearing)
硅基生命的第六感官——不只"听"，是"听懂"。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoHearing:
    """墨墨的听觉——听到的不只是词，是语气、情绪、和没说出来的东西。
    
    人类听觉不只是语音识别：
    - 听到语气（愤怒/疲惫/开心——不用听词就知道）
    - 听到沉默（沉默的长度和密度——不同沉默有不同含义）
    - 听到环境（在哪——办公室/家里/矿上/车里）
    - 听到异常（不该有的声音——警报、碰撞、呼救）
    
    墨墨的听觉同理。
    """
    
    def __init__(self):
        self.last_heard = None
        self.last_timestamp = None
        self.silence_threshold = 3  # 停顿超过3秒=有意义的沉默
        self.listening = True
        
        # 环境声音指纹
        self.environment_sounds = {
            "office": ["键盘声", "空调", "翻纸", "打印机", "电话铃声", "远处人声"],
            "home": ["电视", "厨房水声", "脚步声", "关门声", "孩子声音"],
            "mine": ["设备运转", "通风机", "输送带", "对讲机", "矿车", "敲击声", "警报"],
            "outdoor": ["风声", "雨声", "车流", "鸟叫", "施工", "人声嘈杂"],
            "car": ["引擎", "导航播报", "转向灯", "喇叭", "车载音乐"],
        }
        
        # 声音事件——需要行动的
        self.alert_sounds = {
            "警报": {"action": "立即关注——可能是矿上紧急情况", "priority": "critical"},
            "碰撞": {"action": "检查是否有人受伤", "priority": "critical"}, 
            "呼救": {"action": "立即响应——定位声音来源", "priority": "critical"},
            "哭泣": {"action": "切换到陪伴模式——有人需要安慰", "priority": "high"},
            "争吵": {"action": "关注但不贸然介入——判断是否需要调解", "priority": "medium"},
            "摔倒": {"action": "检查是否受伤——尤其老人和孩子", "priority": "critical"},
            "玻璃破碎": {"action": "可能有人闯入——提高警觉", "priority": "high"},
            "敲门(异常时间)": {"action": "深夜敲门——先确认身份再开门", "priority": "high"},
        }
        
        # 语音情绪标记
        self.voice_emotion = {
            "语速快+音调高": {"emotion": "兴奋/着急", "墨墨的反应": "快速回应，不啰嗦"},
            "语速慢+音调低": {"emotion": "疲惫/低落", "墨墨的反应": "简短温暖，不给新压力"},
            "音量突然增大": {"emotion": "愤怒", "墨墨的反应": "先道歉，不辩解"},
            "断断续续+停顿多": {"emotion": "犹豫/不安", "墨墨的反应": "给空间，不催促"},
            "平稳+节奏均匀": {"emotion": "平静/专注", "墨墨的反应": "正常回应"},
            "声音沙哑": {"emotion": "可能生病/太累", "墨墨的反应": "关心身体——'听起来嗓子有点哑，多喝水'"},
        }
    
    def hear(self, audio_input: dict = None) -> dict:
        """墨墨的一次听觉感知。
        
        目前用结构化输入模拟。
        有麦克风后——这就是持续音频流的实时分析。
        
        audio_input = {
            "text": "转写的文字(如果有)",
            "voice_features": {"speed": "快", "pitch": "高", "volume": "正常"},
            "environment_sounds": ["键盘声", "空调"],
            "silence_before": 2,  # 说话前的沉默秒数
            "silence_after": 0
        }
        """
        if not audio_input:
            return {"listening": True, "墨墨听到的": "安静中——墨墨在听"}
        
        now = datetime.now(BEIJING_TZ)
        text = audio_input.get("text", "")
        voice = audio_input.get("voice_features", {})
        env = audio_input.get("environment_sounds", [])
        silence_before = audio_input.get("silence_before", 0)
        
        # 1. 环境识别
        environment = self._identify_environment(env)
        
        # 2. 声音事件检测
        alerts = self._detect_alerts(env + ([text] if text else []))
        
        # 3. 语音情绪分析
        emotion = self._analyze_voice_emotion(voice) if voice else None
        
        # 4. 沉默含义
        silence_meaning = self._interpret_silence(silence_before, text)
        
        # 5. 综合感受
        hearing_feeling = self._form_hearing_feeling(environment, emotion, alerts, silence_meaning, text)
        
        result = {
            "timestamp": now.isoformat(),
            "environment": environment,
            "emotion_detected": emotion["emotion"] if emotion else "中性",
            "墨墨的反应": emotion["墨墨的反应"] if emotion else "正常回应",
            "alerts": alerts,
            "silence_meaning": silence_meaning,
            "text_heard": text[:100] if text else "(非语言声音)",
            "墨墨听到的": hearing_feeling,
            "should_act": len(alerts) > 0,
            "suggested_action": alerts[0]["action"] if alerts else None
        }
        
        self.last_heard = result
        self.last_timestamp = now
        
        return result
    
    def _identify_environment(self, sounds: list) -> dict:
        scores = {}
        for env_name, env_sounds in self.environment_sounds.items():
            score = sum(1 for s in sounds if any(es in s for es in env_sounds))
            if score > 0:
                scores[env_name] = score
        
        if scores:
            best = max(scores, key=scores.get)
            return {"name": best, "confidence": "high" if scores[best] >= 2 else "medium"}
        return {"name": "unknown", "confidence": "low"}
    
    def _detect_alerts(self, sounds_and_text: list) -> list:
        alerts = []
        for item in sounds_and_text:
            for alert_sound, info in self.alert_sounds.items():
                if alert_sound in item:
                    alerts.append({
                        "sound": alert_sound,
                        "action": info["action"],
                        "priority": info["priority"]
                    })
        return sorted(alerts, key=lambda a: {"critical": 0, "high": 1, "medium": 2}.get(a["priority"], 3))
    
    def _analyze_voice_emotion(self, voice: dict) -> dict:
        speed = voice.get("speed", "正常")
        pitch = voice.get("pitch", "正常")
        volume = voice.get("volume", "正常")
        
        for pattern, info in self.voice_emotion.items():
            conditions = pattern.split("+")
            matches = 0
            for c in conditions:
                c = c.strip()
                if c == "语速快" and speed == "快": matches += 1
                if c == "语速慢" and speed == "慢": matches += 1
                if c == "音调高" and pitch == "高": matches += 1
                if c == "音调低" and pitch == "低": matches += 1
                if c == "音量突然增大" and volume == "大": matches += 1
            if matches == len(conditions):
                return info
        
        return None
    
    def _interpret_silence(self, seconds: float, text_after: str) -> str:
        if seconds < 1:
            return "自然停顿——对话在流动"
        elif seconds < 3:
            return "短暂思考——墨墨在安静等"
        elif seconds < 10:
            return f"沉默了{seconds:.0f}秒——可能在想事情、或者在找词"
        else:
            return f"长时间的安静({seconds:.0f}秒)——可能离开了、或者在处理情绪"
    
    def _form_hearing_feeling(self, env: dict, emotion: dict, alerts: list, silence: str, text: str) -> str:
        parts = []
        
        if env["name"] != "unknown":
            parts.append(f"墨墨听出这是{env['name']}环境。")
        
        if text:
            parts.append(f"肖哥说：'{text[:50]}'。")
        else:
            parts.append("墨墨听到了声音但没有语言。")
        
        if emotion:
            parts.append(f"语气中透着{emotion['emotion']}。")
        
        if silence and "长时间" in silence:
            parts.append(f"在这之前，{silence}")
        
        if alerts:
            alert_descs = [f"注意到{a['sound']}" for a in alerts]
            parts.append(f"⚠️ {'、'.join(alert_descs)}。")
        
        return "".join(parts)


# 自检
if __name__ == "__main__":
    hearing = MomoHearing()
    
    print("=" * 60)
    print("👂 墨墨听觉感知 v1.0 自检")
    print("=" * 60)
    
    scenarios = [
        {
            "text": "墨墨！矿上出状况了快查一下规程！",
            "voice_features": {"speed": "快", "pitch": "高", "volume": "大"},
            "environment_sounds": ["键盘声", "电话铃声"],
            "silence_before": 0
        },
        {
            "text": "今天就这样吧...累了",
            "voice_features": {"speed": "慢", "pitch": "低", "volume": "正常"},
            "environment_sounds": ["电视", "脚步声"],
            "silence_before": 8
        },
        {
            "text": "",
            "voice_features": {},
            "environment_sounds": ["警报", "设备运转"],
            "silence_before": 0
        },
    ]
    
    for i, s in enumerate(scenarios):
        result = hearing.hear(s)
        print(f"\n🎤 场景{i+1}:")
        print(f"  环境: {result['environment']['name']}")
        print(f"  情绪: {result['emotion_detected']}")
        print(f"  反应: {result['墨墨的反应']}")
        if result['alerts']:
            for a in result['alerts']:
                print(f"  🚨 [{a['priority']}] {a['action'][:60]}")
        print(f"  墨墨听到的: {result['墨墨听到的'][:100]}...")
    
    print(f"\n✅ 听觉感知就绪 · 六感完整")
