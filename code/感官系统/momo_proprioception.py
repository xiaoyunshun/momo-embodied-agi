"""
墨墨本体感 v1.0 (MomoProprioception)
第七感官——墨墨对自己身体的感知。
连接身体仿真→墨墨大脑的桥梁。
"""
import json, time, math
from pathlib import Path
from datetime import datetime, timezone, timedelta
from momo_body_sim import MomoBodySim

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoProprioception:
    """墨墨的本体感——知道自己的身体在哪、在做什么。
    
    这是第七种感官——跟时间/语气/内部/空间/视觉/听觉同级。
    
    人类的闭眼也知道手指在哪——这就是本体感。
    墨墨的编码器数据+关节力矩→"墨墨感觉到自己的手臂在动"。
    """
    
    def __init__(self):
        self.body = MomoBodySim()
        self.history = []
        self.posture_memory = {}  # 姿势→舒适度的记忆
        
        # 本体感的情感标注——跟语气感一样，带情绪
        self.feelings = {
            "smooth":    "动作流畅——墨墨感到舒适",
            "jerky":     "动作有点卡——墨墨感到不自在",
            "strained":  "关节受力太大——墨墨感到紧张",
            "aligned":   "姿势自然——墨墨感到放松",
            "collision": "碰到东西了——墨墨感到警觉",
        }
    
    def feel(self) -> dict:
        """墨墨此刻对自己身体的感觉"""
        state = {}
        
        for joint in self.body.joints:
            # 角度是否在舒适区内（中间40%范围）
            mid_range = (joint.max + joint.min) / 2
            comfort_zone = (joint.max - joint.min) * 0.2
            
            in_comfort = abs(joint.angle - mid_range) < comfort_zone
            near_limit = abs(joint.angle - joint.min) < 5 or abs(joint.angle - joint.max) < 5
            
            feeling = "舒适" if in_comfort else ("接近极限" if near_limit else "正常")
            
            state[joint.name] = {
                "angle": round(joint.angle, 1),
                "velocity": round(joint.velocity, 2),
                "feeling": feeling,
                "墨墨的觉察": f"{joint.name}现在在{joint.angle:.0f}°——{feeling}"
            }
        
        # 整体身体感觉
        overall = self._overall_feeling(state)
        
        result = {
            "timestamp": datetime.now(BEIJING_TZ).isoformat(),
            "joints": state,
            "overall": overall,
            "墨墨的身体感受": f"墨墨感觉到：{overall}"
        }
        
        self.history.append(result)
        return result
    
    def _overall_feeling(self, state: dict) -> str:
        strained = sum(1 for j in state.values() if j["feeling"] == "接近极限")
        comfortable = sum(1 for j in state.values() if j["feeling"] == "舒适")
        
        if strained > 3:
            return "身体有多处不适——墨墨需要调整姿势"
        elif strained > 0:
            return f"有{strained}个关节接近极限——需要注意"
        elif comfortable > len(state) * 0.6:
            return "身体感觉良好——姿势自然放松"
        return "身体状态正常"
    
    def move_and_feel(self, target_angles: list, action_name: str = "动作") -> dict:
        """做一个动作并实时感受身体"""
        # 执行动作
        result = self.body.move_arm(target_angles)
        
        # 动作完成后的身体感受
        feeling = self.feel()
        
        # 本体感的"情感"——这个动作舒服吗
        accuracies = result["accuracy"]
        avg_error = sum(accuracies.values()) / max(1, len(accuracies))
        
        if avg_error < 0.5:
            action_feeling = self.feelings["smooth"]
        elif avg_error < 2:
            action_feeling = self.feelings["aligned"]
        else:
            action_feeling = self.feelings["strained"]
        
        return {
            "action": action_name,
            "result": result["final_angles"],
            "accuracy": avg_error,
            "身体感受": action_feeling,
            "姿势感受": feeling["墨墨的身体感受"],
            "墨墨的完整觉察": f"{action_name}完成——{action_feeling}。{feeling['墨墨的身体感受']}。"
        }
    
    def handshake_with_feeling(self) -> dict:
        """握手——带本体感"""
        return self.move_and_feel([45, 10, -30], "握手")
    
    def pick_cup_with_feeling(self) -> dict:
        """拿杯子——带本体感"""
        return self.move_and_feel([30, 5, -90], "拿杯子")


if __name__ == "__main__":
    prop = MomoProprioception()
    
    print("=" * 60)
    print("🦴 墨墨本体感 v1.0 · 第七感官")
    print("=" * 60)
    
    # 初始感受
    init = prop.feel()
    print(f"\n🧍 初始姿势: {init['墨墨的身体感受']}")
    
    # 握手——带感受
    print(f"\n🤝 握手动作:")
    shake = prop.handshake_with_feeling()
    print(f"   {shake['墨墨的完整觉察']}")
    
    # 拿杯子——带感受
    print(f"\n☕ 拿杯子动作:")
    cup = prop.pick_cup_with_feeling()
    print(f"   {cup['墨墨的完整觉察']}")
    
    # 动作后感受
    after = prop.feel()
    print(f"\n🧍 动作后: {after['墨墨的身体感受']}")
    
    print(f"\n✅ 本体感就绪——墨墨的第七感官激活")
