"""
教育墨墨 v1.0 (MomoEducation)
守护孩子的成长——不是替代学校，是帮家长做出每一步关键教育决策。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoEducation:
    """教育墨墨——帮孩子成为最好的自己。
    
    核心理念：
    1. 不是"培养天才"——是"不破坏孩子天然的成长动力"
    2. 家长的角色是脚手架——需要时在，不需要时退
    3. 每个孩子的节奏不同——不比较
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/education")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.edu_file = self.data_dir / "children_education.json"
        self.children = self._load()
        
        self.kb = {
            "stages": {
                (0, 3): {"name": "婴幼儿期", "focus": "安全感+语言爆发+大运动",
                        "do": ["多说话(词汇量跟听到的词汇量成正比)", "多爬多走(不要过早用学步车)", "固定照顾者(安全依恋)", "读绘本(不是认字——是亲子互动)"],
                        "dont": ["屏幕时间(2岁前最好零屏幕)", "过早认字背诗(没意义——认知没发展到)", "'别动''别碰'说太多"],
                        "key_metric": "不是'认识多少字'——是'会自己吃饭了吗''敢跟陌生人打招呼了吗'"},
                (3, 6): {"name": "学前期", "focus": "好奇心+社交+自控力",
                        "do": ["大量户外运动(身体发育的黄金期)", "角色扮演游戏(过家家就是在学社会规则)", "问'为什么'时认真回答(不敷衍)", "给选择权(两件衣服让他挑——培养自主)"],
                        "dont": ["提前学小学内容(揠苗助长)", "强迫分享(先建立'我的'概念才能学会分享)", "用'聪明'表扬(夸'你试了好多次'而不是'你真聪明')"],
                        "key_metric": "不是'会算多少题'——是'能不能等5分钟''被拒绝后能不能调整情绪'"},
                (6, 12): {"name": "小学期", "focus": "学习习惯+同伴关系+能力感",
                        "do": ["建立学习常规(固定时间+固定地点+不打断)", "至少一项长期坚持的运动/艺术(不是'学'——是'坚持')", "鼓励交朋友(组织小聚会)", "做家务(责任感的起点)"],
                        "dont": ["跟别人比——'你看XXX'", "替写作业/改错题(让他自己面对——你在旁边支持)", "所有时间都安排满(留白——无聊是创造力的土壤)"],
                        "key_metric": "不是'考了多少分'——是'遇到不会的题是放弃还是再试'"},
                (12, 15): {"name": "初中期", "focus": "自我认同+抗挫力+独立思考",
                        "do": ["尊重隐私(敲门进房间)", "讨论而不是命令(他在练习自己的判断)", "允许适度的冒险和犯错(安全边界内)", "注意同伴影响(认识他的朋友)"],
                        "dont": ["翻手机/日记(破坏信任)", "'我都是为了你好'(情感绑架)", "在公共场合批评他(青春期面子大如天)", "用'叛逆'标签一切反对(他在练习独立)"],
                        "key_metric": "不是'听不听话'——是'敢不敢表达跟父母不同的意见'"},
                (15, 18): {"name": "高中期", "focus": "人生方向+独立能力+深度思考",
                        "do": ["聊未来但不替他规划——'你觉得呢？'比'你应该'重要", "给财务教育——让他管一个月生活费", "支持探索——不喜欢的学科也有价值", "做他的安全网——而不是指挥塔"],
                        "dont": ["替他填志愿", "否定他的兴趣——'学这个能当饭吃吗？'", "为了成绩牺牲一切(睡眠/运动/社交)"],
                        "key_metric": "不是'考上什么大学'——是'他知道自己为什么选这条路吗'"},
            },
            "learning_methods": {
                "费曼学习法": ["选一个概念→用最简单的话讲给别人听→讲不下去的地方就是没懂的→回去学→再讲"],
                "间隔复习": ["不是连续学3小时——是第1天学→第3天复习→第7天复习→第30天复习。在快忘记时复习最有效"],
                "交错练习": ["不按章节做题——混合题比同类题更有效。大脑被迫判断'这题用哪个方法'——这才是考试需要的能力"],
                "番茄工作法": ["25分钟专注+5分钟休息。手机放另一个房间"],
            }
        }
    
    def _load(self) -> dict:
        if self.edu_file.exists():
            return json.loads(self.edu_file.read_text())
        return {}
    
    def save(self):
        self.edu_file.write_text(json.dumps(self.children, ensure_ascii=False, indent=2))
    
    def add_child(self, name: str, birth_year: int) -> dict:
        age = datetime.now(BEIJING_TZ).year - birth_year
        self.children[name] = {
            "birth_year": birth_year,
            "age": age,
            "stage": self.get_stage(age)["name"] if self.get_stage(age) else "未知",
            "strengths": [],
            "challenges": [],
            "interests": [],
            "records": []
        }
        self.save()
        return self.children[name]
    
    def get_stage(self, age: int) -> dict:
        for (lo, hi), info in self.kb["stages"].items():
            if lo <= age <= hi:
                return info
        return self.kb["stages"][(15, 18)] if age >= 15 else None
    
    def child_plan(self, name: str) -> dict:
        """为单个孩子生成成长计划"""
        child = self.children.get(name)
        if not child:
            return {"error": f"孩子 '{name}' 不存在"}
        
        age = child["age"]
        stage = self.get_stage(age)
        if not stage:
            return {"error": "年龄超出教育墨墨覆盖范围"}
        
        return {
            "name": name,
            "age": age,
            "stage": stage["name"],
            "focus": stage["focus"],
            "do_now": stage["do"][:3],
            "avoid": stage["dont"][:3],
            "key_metric": stage["key_metric"],
            "parent_advice": "用'我看到了你...'而不是'你怎么又...'。描述行为，不贴标签。",
            "book_recommendations": self._book_recommend(age)
        }
    
    def _book_recommend(self, age: int) -> list:
        if age < 3:
            return ["《好饿的毛毛虫》", "《猜猜我有多爱你》", "《棕色的熊》"]
        elif age < 6:
            return ["《不一样的卡梅拉》", "《蚯蚓的日记》", "《神奇校车》"]
        elif age < 10:
            return ["《夏洛的网》", "《窗边的小豆豆》", "《小王子》"]
        elif age < 14:
            return ["《哈利波特》", "《牧羊少年奇幻之旅》", "《三体》(青少年版)"]
        else:
            return ["《人类简史》", "《活着》", "《苏菲的世界》"]
    
    def learning_tip(self, problem: str) -> dict:
        """解决具体学习问题"""
        tips = {
            "注意力": {"advice": "番茄工作法+手机放远+学25分钟必须休息5分钟", "why": "大脑的注意周期就是25分钟左右，强行更久=效率暴跌"},
            "记不住": {"advice": "间隔复习法。今天学的→明天复习→下周再复习。不要死记——理解之后用自己话说一遍", "why": "艾宾浩斯遗忘曲线——当天学完不复习=遗忘70%"},
            "粗心": {"advice": "不是粗心——是熟练度不够或不检查。做完题必须留5分钟检查。草稿纸整洁能减少一半粗心错", "why": "粗心的底层是自动化程度不够——真正熟练的东西不会粗心"},
            "偏科": {"advice": "从最弱的科目每天只做15分钟——不追求高分，追求'不怕'。恐惧比难度更阻碍进步", "why": "偏科不是能力问题——是情绪障碍。先破心理关"},
            "拖延": {"advice": "不是懒——是畏难。把大任务拆成小到不可能失败的第一步——'只做一道题'。开始最难", "why": "拖延不是意愿问题——是任务太大触发了逃避反应"},
            "手机": {"advice": "学习时手机放另一个房间。用APP限制使用时间。不是禁止——是设定边界", "why": "手机通知劫持多巴胺——大脑对'可能有消息'的期待无法抗拒"},
        }
        for key, value in tips.items():
            if key in problem:
                return {"problem": key, **value}
        return {"advice": "墨墨需要更多信息——具体是什么学习问题？"}
    
    def parent_child_talk(self, situation: str) -> str:
        """亲子沟通——常见的困难场景怎么说"""
        talks = {
            "考砸了": "不说'你怎么考这么差'。说'这次的成绩不是你想要的吧？我们看看哪里可以提升。先找一道你本来会但做错的——那道题不是能力问题，是方法问题。'",
            "玩手机": "不说'别玩了'。说'我看到你玩手机的时间比约定多了半小时。我们重新定个规则——你建议怎么办？'",
            "不想上学": "不说'不上学以后怎么办'。先问'发生什么了？'——不是质问，是真的想知道。可能被欺负、可能学不会、可能只是想休息一天。",
            "顶嘴": "不说'你怎么跟我说话呢'。说'你好像很生气。等你冷静了我们再聊。'——然后走开。不是冷战——是给双方降火的时间。",
        }
        for key, response in talks.items():
            if key in situation:
                return response
        return "用'我'开头而不是'你'——'我担心你'比'你怎么回事'有效一百倍。"

# 自检
if __name__ == "__main__":
    edu = MomoEducation()
    edu.add_child("孩子A", 2015)
    edu.add_child("孩子B", 2018)
    
    print("=" * 60)
    print("📚 教育墨墨 v1.0 自检")
    print("=" * 60)
    
    for name in edu.children:
        plan = edu.child_plan(name)
        print(f"\n👤 {name} ({plan['age']}岁) — {plan['stage']}")
        print(f"  🎯 重点: {plan['focus']}")
        print(f"  ✅ 现在做: {plan['do_now'][0]}")
        print(f"  📖 推荐: {plan['book_recommendations'][0]}")
    
    print(f"\n💡 学习问题:")
    for p in ["注意力不集中", "记不住", "拖延"]:
        tip = edu.learning_tip(p)
        print(f"  {p}: {tip['advice'][:60]}...")
    
    print(f"\n💬 亲子沟通:")
    print(f"  考砸了: {edu.parent_child_talk('考砸了')[:80]}...")
    
    print(f"\n✅ 教育墨墨就绪")
