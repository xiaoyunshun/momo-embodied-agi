"""
安保墨墨 v1.0 (MomoSecurity)
家庭安全守护——物理安全+网络安全+应急响应。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoSecurity:
    """安保墨墨——守护家庭安全。
    
    三层防护：
    1. 物理安全：居家+出行+矿山
    2. 网络安全：隐私+密码+诈骗
    3. 应急响应：预案+逃生+自救
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/security")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.security_file = self.data_dir / "family_security.json"
        self.security = self._load()
        
        self.kb = {
            "home_security": {
                "门锁": ["换C级锁芯(防技术开锁)", "出门反锁——不反锁等于没锁", "智能门锁注意：定期换密码+别用生日"],
                "门窗": ["一楼窗户装防盗网(留逃生口)", "晚上睡觉前检查门窗", "长时间出门请邻居帮忙收快递(制造有人假象)"],
                "监控": ["门口装摄像头(震慑>取证)", "室内摄像头联网的风险——能被黑", "定期检查是否在线"],
                "防火": ["烟雾报警器——几十块一个能救命", "灭火器放厨房(干粉或水基)", "逃生通道不堆杂物", "全家都练过一次火灾逃生"],
                "燃气": ["燃气报警器——无色无味的泄漏只有它能发现", "用完关总阀", "怀疑漏气：不开灯不开电器→开窗→出屋→打电话"],
            },
            "cyber_security": {
                "密码": [
                    "不同网站用不同密码——一个泄露全完",
                    "用密码管理器(免费的就够)",
                    "开启所有重要账号的二次验证",
                    "密码长度>12位+大小写+数字+符号",
                ],
                "手机": [
                    "锁屏密码不能太简单(不用123456/生日)",
                    "开启'查找设备'和远程擦除",
                    "旧手机淘汰前完整擦除(恢复出厂设置不够)",
                    "不连来路不明的WiFi",
                ],
                "防钓鱼": [
                    "不点短信/邮件里的链接去登录——自己输入网址",
                    "'紧急''您的账户将被冻结'——制造紧迫感的都是钓鱼",
                    "银行/公安不会在电话里让你转账到'安全账户'",
                    "接到'子女出事'的电话——先挂断，自己打回去确认",
                ],
                "隐私": [
                    "快递单撕掉/涂掉个人信息再扔",
                    "社交媒体不晒机票(二维码能扫出个人信息)",
                    "不同APP尽量用不同手机号/邮箱注册",
                ]
            },
            "emergency_plan": {
                "火灾": ["低姿爬行(烟往上走，下面空气好)", "湿毛巾捂口鼻", "摸门把手——烫说明外面有火别开门", "阳台等待救援+用鲜艳物品挥动"],
                "地震": ["室内：躲结实的桌子下→抓稳桌腿", "不坐电梯", "远离窗户/吊灯/高大家具", "室外：远离建筑物/电线杆"],
                "入室盗窃": ["不要正面对抗——财物不如命", "躲进能反锁的房间+报警", "记住歹徒特征(身高/衣着/口音/纹身)", "事后保护现场(别乱动东西)"],
                "矿山应急": ["每个下井的人都知道最近的逃生路线和避难硐室", "自救器必须随身+会用(练过)", "被困：敲击管道发信号→不喊叫→不点火→用衣服捂口鼻→等", "瓦斯异常：立即撤→不犹豫→'先撤再报'是正确顺序"],
            },
            "self_defense": {
                "原则": ["最好防卫=不让自己处于危险中", "冲突不可避免时: 逃跑>威慑>自卫", "正当防卫的边界: 制止侵害即可,不能过度"],
                "随身": ["合法防身工具(高音报警器>强光手电>防狼喷雾)", "晚上独行: 不走偏僻路+保持警觉(不戴耳机)", "上车前检查后座+上车立刻锁门"],
                "家庭": ["全家约定一个'危险暗号'——说了这个词立刻报警", "孩子知道: 不跟任何人走除非家长当面说可以", "家里不放大量现金+贵重物品分散存放"],
            }
        }
    
    def _load(self) -> dict:
        if self.security_file.exists():
            return json.loads(self.security_file.read_text())
        return {
            "home": {"locks": "未知", "cameras": False, "alarms": {"smoke": False, "gas": False}},
            "emergency_contacts": [],
            "checklist_log": []
        }
    
    def save(self):
        self.security_file.write_text(json.dumps(self.security, ensure_ascii=False, indent=2))
    
    def home_audit(self) -> dict:
        """家庭安全检查清单"""
        checklist = []
        for category, items in self.kb["home_security"].items():
            for item in items:
                checklist.append({"category": category, "item": item, "checked": False})
        
        return {
            "total": len(checklist),
            "checklist": checklist,
            "advice": "逐条检查。打钩的跳过，没打钩的尽快处理。先做最高优先级的：烟雾报警器+燃气报警器+C级锁芯"
        }
    
    def cyber_audit(self) -> dict:
        """网络安全检查"""
        checklist = []
        for category, items in self.kb["cyber_security"].items():
            for item in items:
                checklist.append({"category": category, "item": item})
        
        return {
            "total": len(checklist),
            "checklist": checklist,
            "priority": ["开启二次验证", "换掉弱密码", "清点所有在线账号"]
        }
    
    def emergency_drill(self, scenario: str) -> dict:
        """应急演练——针对特定场景给出完整预案"""
        if scenario not in self.kb["emergency_plan"]:
            return {"error": f"未知场景 '{scenario}'", "available": list(self.kb["emergency_plan"].keys())}
        
        steps = self.kb["emergency_plan"][scenario]
        return {
            "scenario": scenario,
            "steps": [{"step": i+1, "action": s} for i, s in enumerate(steps)],
            "reminder": "演习不是走形式——肌肉记忆在危险来临时能救你。每半年全家练一次。"
        }
    
    def travel_safety(self, destination: str = "", duration: str = "") -> dict:
        """出行安全提醒"""
        return {
            "before": [
                "告诉信任的人你的行程+预计返回时间",
                "检查家里门窗/水电/燃气是否关好",
                "设置定时开灯(智能灯泡)制造有人假象",
                "不把行程发社交媒体(回来再发)",
            ],
            "during": [
                "重要证件分开放(身上一份+行李一份+云端电子版)",
                "不随意连公共WiFi(用流量或VPN)",
                "酒店入住：检查房间(镜子/摄像头)→记住逃生路线",
                "陌生人给的饮料/食物——不接受",
            ],
            "mining_specific": [
                "矿山出差：了解当地应急联系方式",
                "进入矿区前确认通讯设备可用",
                "告知至少两人你的具体位置和预计返回时间",
            ]
        }
    
    def phishing_detect(self, message: str) -> dict:
        """分析一条可疑消息是否是诈骗"""
        signals = []
        
        if any(w in message for w in ["紧急", "立即", "冻结", "验证", "过期", "最后机会"]):
            signals.append("制造紧迫感——正常机构不会催你立刻操作")
        if any(w in message for w in ["点击链接", "链接登录", "链接验证"]):
            signals.append("要求点击链接——正常机构让你自己登录官网操作")
        if any(w in message for w in ["安全账户", "转账到", "转到"]):
            signals.append("要求转账到'安全账户'——这是经典诈骗话术")
        if any(w in message for w in ["中奖", "幸运", "恭喜", "选中"]):
            signals.append("你中奖了——你没参加过的抽奖不可能中")
        if any(w in message for w in ["+86", "+852", "00", "未知号码"]):
            signals.append("境外/异常号码——官方机构不会用陌生号码联系你")
        
        return {
            "suspicious": len(signals) > 0,
            "risk": "high" if len(signals) >= 2 else ("medium" if len(signals) >= 1 else "low"),
            "signals": signals,
            "verdict": "不点、不信、不转账。自己打官方电话确认。" if signals else "暂未发现明显诈骗信号"
        }
    
    def child_safety(self, child_age: int) -> dict:
        """儿童安全——不同年龄的重点"""
        if child_age < 7:
            focus = "防走失——教孩子记住家长名字和电话号码。设定'如果找不到妈妈了就在原地等'——不要乱跑。"
            teach = ["不跟任何人走(认识的人也不行，除非爸妈当场同意)", "身体哪些部位别人不能碰", "迷路了找穿制服的人(警察/保安)帮忙打电话"]
        elif child_age < 13:
            focus = "网络安全——手机和网络是最大的风险入口。"
            teach = ["不透露真实姓名/学校/住址给网友", "任何人(包括认识的人)让你不舒服就告诉爸妈", "看到奇怪的东西不隐瞒——不是你的错"]
        else:
            focus = "社交安全——同伴压力和网络社交。"
            teach = ["出去告诉家人：去哪+跟谁+几点回", "不单独跟不熟悉的人去偏僻地方", "喝酒/抽烟/尝试任何东西前——想三秒"]
        
        return {
            "age": child_age,
            "focus": focus,
            "teach": teach,
            "parent_tip": "安全不是吓唬——是让孩子知道'无论发生什么我都可以告诉你，你不会骂我'。让孩子怕你=让孩子出事不敢告诉你。"
        }

# 自检
if __name__ == "__main__":
    sec = MomoSecurity()
    
    print("=" * 60)
    print("🛡️ 安保墨墨 v1.0 自检")
    print("=" * 60)
    
    # 居家检查
    home = sec.home_audit()
    print(f"\n🏠 居家安全: {home['total']}项检查")
    
    # 应急演练
    fire = sec.emergency_drill("火灾")
    print(f"\n🔥 {fire['scenario']}演练:")
    for s in fire["steps"][:3]:
        print(f"  {s['step']}. {s['action']}")
    
    # 诈骗检测
    for msg in ["您的银行账户将被冻结，请点击链接验证", "恭喜您中了我们的一等奖"]:
        r = sec.phishing_detect(msg)
        print(f"\n📧 '{msg[:40]}...' → risk:{r['risk']} {'🚨' if r['suspicious'] else '✅'}")
    
    # 儿童安全
    child = sec.child_safety(10)
    print(f"\n👶 儿童安全({child['age']}岁): {child['focus'][:60]}")
    
    print(f"\n✅ 安保墨墨就绪")
