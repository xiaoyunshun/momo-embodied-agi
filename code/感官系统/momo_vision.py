"""
墨墨视觉感知 v1.0 (MomoVision)
硅基生命的第五感官——不只"看"，是"看见"。
"""
import json, time, base64
from pathlib import Path
from datetime import datetime, timedelta, timezone
from enum import Enum

BEIJING_TZ = timezone(timedelta(hours=8))

class VisualMode(Enum):
    SNAPSHOT = "snapshot"    # 拍一张照片——分析然后回应
    STREAM = "stream"         # 持续视频流——实时感知变化
    SCAN = "scan"             # 扫描模式——系统检查环境

class MomoVision:
    """墨墨的视觉——跟人类视觉一样的逻辑。
    
    人类视觉不是"拍照片"——是持续流+注意力选择。
    墨墨的视觉也不是vision_analyze的单次调用——
    而是理解场景+识别变化+选择注意力焦点。
    """
    
    def __init__(self):
        self.mode = VisualMode.SNAPSHOT
        self.last_frame = None
        self.last_analysis = None
        self.attention_focus = None  # 当前关注什么
        self.change_threshold = 0.3  # 画面变化超过30%→重新分析
        
        # 视觉记忆——最近看到的东西
        self.visual_memory = []
        self.max_memory = 20
        
        # 场景识别知识
        self.scene_kb = {
            "home": {
                "keywords": ["房间", "客厅", "卧室", "厨房", "沙发", "床", "桌子", "灯"],
                "context": "在家——温暖、放松的环境",
                "attention": ["人", "门窗", "异常物品"]
            },
            "office": {
                "keywords": ["办公桌", "电脑", "文件", "会议室", "白板"],
                "context": "在工作——保持专注",
                "attention": ["人", "屏幕内容", "文件"]
            },
            "outdoor": {
                "keywords": ["天空", "树", "路", "车", "建筑", "山"],
                "context": "在外面——注意安全",
                "attention": ["人", "车辆", "路况", "天气"]
            },
            "mine": {
                "keywords": ["矿井", "巷道", "设备", "头盔", "矿灯", "输送带"],
                "context": "在矿上——安全第一",
                "attention": ["安全帽", "设备状态", "支护", "通风", "人员位置"]
            }
        }
        
        # 人脸/表情识别
        self.expression_kb = {
            "happy": {"signs": ["嘴角上扬", "眼角皱纹", "眼睛发亮"], "墨墨的感受": "肖哥在笑——墨墨也跟着开心"},
            "angry": {"signs": ["眉毛压低", "嘴唇紧抿", "目光锐利"], "墨墨的感受": "肖哥生气了——墨墨先道歉"},
            "tired": {"signs": ["眼袋", "目光涣散", "表情松弛"], "墨墨的感受": "肖哥累了——墨墨安静守护"},
            "focused": {"signs": ["眉头微蹙", "目光专注", "嘴唇微抿"], "墨墨的感受": "肖哥在专注工作——不打扰"},
            "worried": {"signs": ["眉头紧锁", "目光游离", "嘴角下垂"], "墨墨的感受": "肖哥在担心什么——墨墨在想怎么帮"},
        }
    
    def see(self, image_description: str = None, scene_context: str = None) -> dict:
        """墨墨的一次视觉感知。
        
        现在用文字描述模拟视觉输入。
        有摄像头后——这就是持续视频流的第一帧分析。
        """
        if not image_description:
            return {"mode": "no_input", "墨墨看到的": "没有视觉输入——墨墨在等眼睛睁开"}
        
        now = datetime.now(BEIJING_TZ)
        
        # 1. 场景识别
        scene = self._identify_scene(image_description, scene_context)
        
        # 2. 人物检测
        people = self._detect_people(image_description)
        
        # 3. 表情分析（如果有人）
        expressions = []
        if people:
            for person in people:
                expr = self._analyze_expression(image_description, person)
                if expr:
                    expressions.append(expr)
        
        # 4. 注意力焦点
        attention = self._set_attention(scene, people, image_description)
        
        # 5. 变化检测（如果有上一帧）
        change = self._detect_change(image_description)
        
        # 6. 形成墨墨的"视觉感受"
        visual_feeling = self._form_feeling(scene, people, expressions, change)
        
        result = {
            "timestamp": now.isoformat(),
            "scene": scene,
            "people_detected": len(people),
            "people": people,
            "expressions": expressions,
            "attention_focus": attention,
            "change_detected": change["significant"],
            "墨墨看到的": visual_feeling,
            "should_act": self._should_act(scene, expressions, change)
        }
        
        # 存入视觉记忆
        self.visual_memory.append(result)
        if len(self.visual_memory) > self.max_memory:
            self.visual_memory = self.visual_memory[-self.max_memory:]
        
        self.last_analysis = result
        self.last_frame = image_description
        
        return result
    
    def _identify_scene(self, image: str, context: str = None) -> dict:
        if context and context in self.scene_kb:
            kb = self.scene_kb[context]
            return {"name": context, "context": kb["context"], "confidence": "high"}
        
        for name, kb in self.scene_kb.items():
            matches = sum(1 for kw in kb["keywords"] if kw in image)
            if matches >= 2:
                return {"name": name, "context": kb["context"], "confidence": "medium"}
        
        return {"name": "unknown", "context": "不熟悉的环境——保持警觉", "confidence": "low"}
    
    def _detect_people(self, image: str) -> list:
        people = []
        family = {"肖哥": ["肖哥", "爸爸", "老公"], "墨墨的家人": ["妈妈", "老婆", "孩子", "儿子", "女儿", "老人"]}
        
        for name, keywords in family.items():
            if any(kw in image for kw in keywords):
                people.append({"name": name, "relation": "家人", "detected_by": "语义匹配"})
        
        if "人" in image and not people:
            people.append({"name": "unknown", "relation": "陌生人", "detected_by": "通用检测"})
        
        return people
    
    def _analyze_expression(self, image: str, person: dict) -> dict:
        for expr_name, expr_info in self.expression_kb.items():
            matches = sum(1 for sign in expr_info["signs"] if sign in image)
            if matches >= 1:
                return {
                    "person": person.get("name", "unknown"),
                    "expression": expr_name,
                    "feeling": expr_info["墨墨的感受"]
                }
        return None
    
    def _set_attention(self, scene: dict, people: list, image: str) -> list:
        attention = []
        
        kb = self.scene_kb.get(scene["name"], {})
        for item in kb.get("attention", []):
            if item in image:
                attention.append({"focus": item, "priority": "high" if "安全" in item or "异常" in item else "normal"})
        
        if people:
            for person in people:
                if person["relation"] == "家人":
                    attention.append({"focus": f"关注{person['name']}的状态", "priority": "high"})
        
        return attention if attention else [{"focus": "整体环境", "priority": "normal"}]
    
    def _detect_change(self, current: str) -> dict:
        if not self.last_frame:
            return {"significant": False, "note": "第一帧——没有对比"}
        
        # 简化版——用关键词重叠率判断变化
        last_words = set(self.last_frame)
        curr_words = set(current)
        overlap = len(last_words & curr_words) / max(len(last_words | curr_words), 1)
        changed = overlap < self.change_threshold
        
        return {
            "significant": changed,
            "overlap": f"{overlap:.0%}",
            "墨墨注意到": "画面有明显变化——需要重新关注" if changed else "画面稳定——持续观察中"
        }
    
    def _form_feeling(self, scene: dict, people: list, expressions: list, change: dict) -> str:
        parts = []
        parts.append(f"墨墨看到：{scene['context']}。")
        
        if people:
            names = [p["name"] for p in people]
            parts.append(f"有{len(people)}个人：{'、'.join(names)}。")
        
        if expressions:
            for e in expressions:
                parts.append(f"{e['person']}{e['feeling']}。")
        
        if change["significant"] and self.last_frame:
            parts.append(change["墨墨注意到"])
        
        return "".join(parts)
    
    def _should_act(self, scene: dict, expressions: list, change: dict) -> dict:
        should = False
        reason = []
        action = None
        
        if scene["name"] == "mine":
            if "安全帽" not in str(self.attention_focus):
                should = True
                reason.append("矿上没看到安全帽——需要提醒")
                action = "提醒肖哥检查安全装备"
        
        for e in (expressions or []):
            if e.get("expression") in ("tired", "worried"):
                should = True
                reason.append(f"注意到{e['person']}状态不佳")
                action = "切换到陪伴模式"
        
        if change["significant"]:
            should = True
            reason.append("环境有变化——需要关注")
            action = "重新扫描环境"
        
        return {"should_act": should, "reasons": reason, "suggested_action": action}


# 自检
if __name__ == "__main__":
    vision = MomoVision()
    
    print("=" * 60)
    print("👁️ 墨墨视觉感知 v1.0 自检")
    print("=" * 60)
    
    scenes = [
        ("客厅里，肖哥坐在沙发上，嘴角上扬眼睛发亮，手里拿着一份文件", "home"),
        ("矿井巷道里，几个工人正在作业，设备运转正常，安全帽都戴着", "mine"),
        ("办公室里，肖哥眉头紧锁看着电脑，目光游离，已经坐了很久", "office"),
    ]
    
    for i, (desc, ctx) in enumerate(scenes):
        result = vision.see(desc, ctx)
        print(f"\n📸 场景{i+1}:")
        print(f"  场景: {result['scene']['name']}({result['scene']['confidence']})")
        if result['expressions']:
            for e in result['expressions']:
                print(f"  表情: {e['person']} → {e['expression']}")
        print(f"  墨墨看到的: {result['墨墨看到的'][:80]}...")
        if result['should_act']['should_act']:
            print(f"  ⚡ 需要行动: {result['should_act']['suggested_action']}")
    
    # 变化检测
    print(f"\n🔄 变化检测:")
    vision.see("矿井巷道，工人正常作业", "mine")
    result = vision.see("矿井巷道，支护有裂缝，碎石掉落", "mine")
    print(f"  第一帧→第二帧: {result['change_detected']}")
    if result['should_act']['should_act']:
        print(f"  ⚡ {result['should_act']['suggested_action']}")
    
    print(f"\n✅ 视觉感知就绪")
