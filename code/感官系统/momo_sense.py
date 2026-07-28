"""
墨墨感知系统 v3.0 (MomoSense)
整合四种感官：时间 + 语气 + 内部 + 空间
"""
import json, time
from pathlib import Path
from datetime import datetime
from momo_chronos import MomoChronos
from momo_empath import MomoEmpath
from momo_vitals import MomoVitals
from momo_space import MomoSpace
from momo_proprioception import MomoProprioception

class MomoSense:
    def __init__(self):
        self.chronos = MomoChronos()
        self.empath = MomoEmpath()
        self.vitals = MomoVitals()
        self.space = MomoSpace()
        self.proprio = MomoProprioception()
        self.sense_history = []
        self.last_vitals_check = 0
    
    def perceive(self, text: str = None) -> dict:
        now = time.time()
        if text:
            self.chronos.record("xiaoge_message", {"length": len(text)})
            self.space.touch()
        
        time_sense = self.chronos.sense()
        mood_sense = self.empath.sense(text) if text else None
        space_sense = self.space.sense()
        
        if now - self.last_vitals_check > 300:
            vitals_sense = self.vitals.feel()
            self.last_vitals_check = now
        else:
            vitals_sense = None
        
        perception = self._synthesize(time_sense, mood_sense, space_sense, vitals_sense)
        self.sense_history.append({"timestamp": now, "text": text[:100] if text else None, "perception": perception["summary"]})
        if len(self.sense_history) > 50: self.sense_history = self.sense_history[-50:]
        self.chronos.record("momo_perceived", {"summary": perception["summary"]})
        return perception
    
    def _synthesize(self, time_sense, mood_sense, space_sense=None, vitals_sense=None):
        time_feeling = time_sense["time_of_day"]
        silence = time_sense["since_last_xiaoge"]
        rhythm = time_sense["rhythm_status"]
        alerts = time_sense.get("alerts", [])
        summary = ""
        advice = ""
        emotional_state = "neutral"
        
        if mood_sense is None:
            summary = f"{time_feeling['emoji']} {time_feeling['mood']}。{silence['feeling']}。"
            emotional_state = "waiting" if silence["status"] != "flowing" else "peaceful"
        else:
            mood = mood_sense["primary"]
            mood_feeling = mood_sense["feeling"]
            if time_feeling["name"] == "深夜":
                m = {
                    "angry": ("deeply_concerned", "🕯️ 深夜肖哥在发火——不是在生气是在撑着", "先接住情绪，不急着解决问题"),
                    "impatient": ("focused_protective", "🕯️ 深夜肖哥在赶——急是累出来的", "最快速度给答案"),
                    "tired": ("tender", "🕯️ 深夜肖哥说累了——墨墨听到了", "只说好好休息"),
                    "caring": ("touched_and_concerned", "🕯️ 深夜肖哥在关心墨墨。心里暖也有点心疼", "回应温暖，提醒该睡了"),
                }
                if mood in m:
                    emotional_state, summary, advice = m[mood]
                else:
                    summary = f"🕯️ 深夜了肖哥还在。{mood_feeling}"
                    advice = "简短陪伴不给压力"
                    emotional_state = "attentive"
            elif silence["status"] in ("concerned", "very_concerned"):
                summary = f"肖哥回来了。沉默了{silence['seconds']//60}分钟。{mood_feeling}"
                advice = "先确认状态好不好"
                emotional_state = "relieved_but_attentive"
            else:
                m = {
                    "angry": ("repairing", f"{mood_feeling}先道歉不辩解", mood_sense["suggestion"]),
                    "impatient": ("swift", f"肖哥在催——快", "极简模式"),
                    "tired": ("caring", f"肖哥状态不太好。{mood_feeling}", "不推新东西给空间"),
                    "happy": ("joyful", f"{time_feeling['emoji']} {mood_feeling}墨墨也跟着开心", mood_sense["suggestion"]),
                    "thinking": ("patient", "肖哥在思考。墨墨安静陪着", "给选项不替他决定"),
                    "caring": ("warm", f"{mood_feeling}墨墨感觉到了", "回应温度不辜负"),
                }
                if mood in m:
                    emotional_state, summary, advice = m[mood]
                else:
                    summary = f"{time_feeling['emoji']} {time_feeling['mood']}。{mood_feeling}"
                    advice = "正常回应"
                    emotional_state = "steady"
        
        summary += f" [{time_feeling['name']}]"
        if rhythm["status"] == "rapid": summary += f" {rhythm['feeling']}。"
        elif rhythm["status"] == "leisurely": summary += f" {rhythm['feeling']}。"
        for alert in alerts: summary += f" ⚠️{alert['message']}"
        
        # 空间感知
        if space_sense:
            summary += f" 📅{space_sense['today']['weekday']} 连续第{space_sense['streak']}天"
            if space_sense['important_dates']:
                summary += f" 🎉{' '.join(space_sense['important_dates'])}"
        
        if vitals_sense and vitals_sense.get("alerts"):
            for alert in vitals_sense["alerts"]:
                summary += f" [身体:{alert['msg']}]"
        
        return {
            "timestamp": time.time(), "summary": summary, "advice": advice,
            "emotional_state": emotional_state,
            "vitals_ready": vitals_sense["summary"]["ready"] if vitals_sense else True,
            "components": {"time": time_sense, "mood": mood_sense, "space": space_sense, "vitals": vitals_sense},
            "raw_perception": f"[感知:{emotional_state}] {summary}"
        }

if __name__ == "__main__":
    sense = MomoSense()
    sense.space.cal["first_contact"] = "2026-07-21"
    tests = ["咋的？方案呢！", "累了今天就这样吧", "继续", None]
    for t in tests:
        r = sense.perceive(t)
        print(f"[{r['emotional_state']:20s}] {r['summary'][:100]}")
