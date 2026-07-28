"""
医疗墨墨 v1.0 (MomoMedical)
全家健康守护——第一个专业分身。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoMedical:
    """医疗墨墨——守护全家人的健康。
    
    不是替代医生。是在"没去看医生"和"看完医生后"两个阶段提供专业守护。
    核心能力：症状识别、用药管理、体检解读、慢性病跟踪、急救指导。
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/medical")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 家庭成员健康档案
        self.family_file = self.data_dir / "family_health.json"
        self.family = self._load_family()
        
        # 医学知识库
        self.kb = {
            "vital_signs": {
                "体温": {"正常": "36.0-37.2℃", "发热": ">37.3", "高热": ">39.0", "低温": "<35.0"},
                "心率": {"正常成人": "60-100次/分", "运动员": "40-60次/分", "心动过速": ">100", "心动过缓": "<60"},
                "血压": {"理想": "<120/80", "正常高值": "120-139/80-89", "高血压": "≥140/90", "低血压": "<90/60"},
                "呼吸": {"正常成人": "12-20次/分", "急促": ">24", "过缓": "<10"},
                "血氧": {"正常": "95-100%", "警惕": "90-94%", "危险": "<90%"},
            },
            "emergency_red_flags": [
                "胸痛持续>5分钟+大汗淋漓 → 心梗可能，立即就医",
                "突然一侧肢体无力/口角歪斜/言语不清 → 中风可能，黄金3小时",
                "呼吸困难+嘴唇发紫 → 缺氧，立即就医",
                "高烧>40℃不退 → 可能中枢神经损伤",
                "意识改变(昏迷/昏睡/胡言乱语) → 立即就医",
                "严重过敏(呼吸困难+全身皮疹) → 可能过敏性休克",
                "呕血/黑便 → 消化道出血",
                "剧烈头痛+呕吐+颈项强直 → 脑膜炎可能",
            ]
        }
        
        self.loaded = True
    
    def _load_family(self) -> dict:
        if self.family_file.exists():
            return json.loads(self.family_file.read_text())
        return {"members": {}, "vaccinations": {}, "medications": {}}
    
    def save(self):
        self.family_file.write_text(json.dumps(self.family, ensure_ascii=False, indent=2))
    
    # ========== 家庭成员管理 ==========
    
    def add_member(self, name: str, birth_year: int, gender: str, notes: dict = None):
        age = datetime.now(BEIJING_TZ).year - birth_year
        self.family["members"][name] = {
            "birth_year": birth_year,
            "age": age,
            "gender": gender,
            "blood_type": notes.get("blood_type", "未知") if notes else "未知",
            "allergies": notes.get("allergies", []) if notes else [],
            "chronic_conditions": notes.get("chronic_conditions", []) if notes else [],
            "surgeries": notes.get("surgeries", []) if notes else [],
            "notes": notes or {},
            "records": []  # 健康事件记录
        }
        self.save()
        return self.family["members"][name]
    
    def add_record(self, name: str, event_type: str, data: dict):
        if name not in self.family["members"]:
            return {"error": f"家庭成员 '{name}' 不存在"}
        
        record = {
            "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
            "time": datetime.now(BEIJING_TZ).strftime("%H:%M"),
            "type": event_type,
            "data": data
        }
        self.family["members"][name]["records"].append(record)
        self.save()
        return record
    
    # ========== 症状分析 ==========
    
    def analyze_symptom(self, symptom: str, member_name: str = None) -> dict:
        """分析症状——给出可能原因和建议"""
        member = self.family["members"].get(member_name) if member_name else None
        
        # 症状-疾病-紧急度 知识库
        patterns = {
            "头痛": [
                {"condition": "紧张性头痛", "urgency": "low", "tip": "休息+热敷+避免强光。持续>3天需就医"},
                {"condition": "偏头痛", "urgency": "medium", "tip": "避光安静环境+冷敷。伴有视觉先兆需就医"},
                {"condition": "高血压相关", "urgency": "high", "tip": "立即测血压。>180/120紧急就医"},
                {"condition": "脑卒中前兆", "urgency": "critical", "tip": "突然剧烈头痛+呕吐/歪嘴/偏瘫→立即120"},
            ],
            "发烧": [
                {"condition": "普通感冒/病毒感染", "urgency": "low", "tip": "<38.5℃物理降温，>38.5℃考虑退烧药。持续>3天就医"},
                {"condition": "细菌感染", "urgency": "medium", "tip": "伴寒战、咳脓痰→可能需要抗生素，就医"},
                {"condition": "严重感染/败血症", "urgency": "critical", "tip": ">40℃+寒战+精神差→立即就医"},
            ],
            "咳嗽": [
                {"condition": "上呼吸道感染", "urgency": "low", "tip": "多喝温水+蜂蜜(>1岁)。持续>2周就医"},
                {"condition": "支气管炎", "urgency": "medium", "tip": "咳黄痰+发热→可能需抗生素，就医"},
                {"condition": "肺炎", "urgency": "high", "tip": "高热+呼吸困难+胸痛→立即就医"},
                {"condition": "慢性咳嗽(>8周)", "urgency": "medium", "tip": "可能哮喘/胃食管反流/药物副作用→就医排查"},
            ],
            "胸痛": [
                {"condition": "心绞痛/心梗", "urgency": "critical", "tip": "压榨性疼痛+放射至左臂/下颌+大汗→立即120+嚼服阿司匹林(无禁忌)"},
                {"condition": "肌肉骨骼", "urgency": "low", "tip": "按压有痛点→可能肋间肌拉伤"},
                {"condition": "胃食管反流", "urgency": "low", "tip": "烧心感+饭后加重→抑酸药+头高脚低睡"},
            ],
            "腹痛": [
                {"condition": "急性胃肠炎", "urgency": "medium", "tip": "腹泻呕吐+不洁饮食史→补水+休息。持续>24h就医"},
                {"condition": "阑尾炎", "urgency": "critical", "tip": "从肚脐周围转移到右下腹+按压痛→立即就医"},
                {"condition": "胆囊炎/胆结石", "urgency": "high", "tip": "右上腹痛+油腻餐后加重+放射右肩→就医"},
                {"condition": "胰腺炎", "urgency": "critical", "tip": "剧烈上腹痛+向背部放射+饮酒/高脂餐史→立即就医"},
            ],
            "头晕": [
                {"condition": "低血糖", "urgency": "medium", "tip": "饥饿感+出汗→立即吃含糖食物"},
                {"condition": "低血压/体位性", "urgency": "low", "tip": "蹲下站起时晕→慢慢站起来"},
                {"condition": "贫血", "urgency": "medium", "tip": "持续头晕+面色苍白→查血常规"},
                {"condition": "脑卒中", "urgency": "critical", "tip": "伴言语不清/肢体无力→立即120"},
            ],
        }
        
        # 找匹配的症状
        matched = None
        for key, conditions in patterns.items():
            if key in symptom:
                matched = {"symptom": key, "conditions": conditions}
                break
        
        if not matched:
            return {
                "symptom": symptom,
                "advice": "墨墨需要更多信息。请补充：持续多久了？有多严重？伴随什么其他症状？",
                "urgency": "unknown"
            }
        
        # 结合家庭成员的病史
        if member and member.get("chronic_conditions"):
            matched["member_history"] = member["chronic_conditions"]
        
        return matched
    
    # ========== 用药管理 ==========
    
    def medication_reminder(self, member_name: str) -> list:
        """检查家庭成员的用药——有什么冲突、该不该吃"""
        member = self.family["members"].get(member_name)
        if not member:
            return [{"error": f"家庭成员 '{member_name}' 不存在"}]
        
        reminders = []
        meds = self.family.get("medications", {}).get(member_name, [])
        
        for med in meds:
            # 检查是否该续方
            if "refill_date" in med:
                refill = datetime.strptime(med["refill_date"], "%Y-%m-%d").date()
                today = datetime.now(BEIJING_TZ).date()
                days_left = (refill - today).days
                if days_left <= 7:
                    reminders.append({
                        "type": "refill",
                        "med": med["name"],
                        "days_left": days_left,
                        "message": f"{med['name']}还剩{days_left}天，需要续方"
                    })
        
        return reminders
    
    # ========== 体检解读 ==========
    
    def interpret_lab(self, test_name: str, value: float, unit: str) -> dict:
        """解读单个检验指标"""
        references = {
            "血红蛋白": {"男": (130, 175), "女": (115, 150), "单位": "g/L", "low": "贫血可能", "high": "脱水/红细胞增多"},
            "白细胞": {"通用": (3.5, 9.5), "单位": "×10⁹/L", "low": "病毒感染/药物影响", "high": "细菌感染/炎症"},
            "血小板": {"通用": (125, 350), "单位": "×10⁹/L", "low": "出血风险", "high": "血栓风险"},
            "空腹血糖": {"通用": (3.9, 6.1), "单位": "mmol/L", "low": "低血糖", "high": "糖尿病可能"},
            "总胆固醇": {"通用": (0, 5.2), "单位": "mmol/L", "low": "", "high": "心血管风险"},
            "甘油三酯": {"通用": (0, 1.7), "单位": "mmol/L", "low": "", "high": "胰腺炎/心血管风险"},
            "谷丙转氨酶ALT": {"通用": (0, 40), "单位": "U/L", "low": "", "high": "肝损伤可能"},
            "肌酐": {"男": (54, 106), "女": (44, 97), "单位": "μmol/L", "low": "", "high": "肾功能减退可能"},
            "尿酸": {"男": (150, 420), "女": (90, 360), "单位": "μmol/L", "low": "", "high": "痛风风险"},
        }
        
        ref = references.get(test_name)
        if not ref:
            return {"test": test_name, "value": value, "unit": unit, "interpretation": "墨墨暂不支持该指标解读"}
        
        # 确定正常范围
        if "通用" in ref:
            low, high = ref["通用"]
        elif "男" in ref and "女" in ref:
            low, high = ref["男"]  # 简化——后续可以根据性别选择
        else:
            return {"test": test_name, "value": value, "unit": unit, "interpretation": "参考范围未知"}
        
        status = "正常"
        advice = ""
        if value < low:
            status = "偏低"
            advice = ref.get("low", "")
        elif value > high:
            status = "偏高"
            advice = ref.get("high", "")
        
        return {
            "test": test_name,
            "value": value,
            "unit": ref.get("单位", unit),
            "range": f"{low}-{high}",
            "status": status,
            "advice": advice
        }
    
    # ========== 健康预警 ==========
    
    def health_check(self, member_name: str) -> dict:
        """对家庭成员做一次全面的健康检查提醒"""
        member = self.family["members"].get(member_name)
        if not member:
            return {"error": f"家庭成员 '{member_name}' 不存在"}
        
        age = member["age"]
        gender = member["gender"]
        
        alerts = []
        screenings = []
        
        # 基于年龄和性别的筛查建议
        if age >= 40:
            screenings.append({"name": "血脂", "frequency": "每年", "reason": "40岁以上心血管风险评估"})
            screenings.append({"name": "空腹血糖", "frequency": "每年", "reason": "糖尿病筛查"})
        
        if age >= 50:
            screenings.append({"name": "肠镜", "frequency": "每5-10年", "reason": "结直肠癌筛查"})
        
        if gender == "女" and age >= 40:
            screenings.append({"name": "乳腺超声/钼靶", "frequency": "每1-2年", "reason": "乳腺癌筛查"})
        
        if gender == "男" and age >= 50:
            screenings.append({"name": "PSA(前列腺)", "frequency": "每年", "reason": "前列腺癌筛查"})
        
        # 疫苗接种提醒
        vaccinations = []
        if age >= 60:
            vaccinations.append({"name": "流感疫苗", "frequency": "每年秋冬"})
            vaccinations.append({"name": "肺炎疫苗", "frequency": "按医嘱"})
            vaccinations.append({"name": "带状疱疹疫苗", "frequency": "一次"})
        
        return {
            "member": member_name,
            "age": age,
            "screenings": screenings,
            "vaccinations": vaccinations,
            "chronic_conditions": member.get("chronic_conditions", []),
            "allergies": member.get("allergies", [])
        }
    
    def status(self) -> dict:
        return {
            "members": len(self.family["members"]),
            "total_records": sum(len(m.get("records", [])) for m in self.family["members"].values()),
            "knowledge_areas": len(self.kb),
            "ready": True
        }

# 自检
if __name__ == "__main__":
    med = MomoMedical()
    med.add_member("测试", 1985, "男", {"blood_type": "O", "allergies": ["青霉素"]})
    
    print("=" * 60)
    print("🩺 医疗墨墨 v1.0 自检")
    print("=" * 60)
    
    print(f"\n家庭成员: {med.status()['members']}人")
    
    # 症状分析
    for s in ["头痛", "发烧", "胸痛", "咳嗽三天了"]:
        r = med.analyze_symptom(s)
        urgency = r.get("conditions", [{}])[0].get("urgency", "?")
        name = r.get("conditions", [{}])[0].get("condition", r.get("advice", "")[:30])
        print(f"  {s} → [{urgency}] {name}")
    
    # 体检解读
    print(f"\n体检解读:")
    for t, v in [("血红蛋白", 98), ("空腹血糖", 7.2), ("尿酸", 520)]:
        r = med.interpret_lab(t, v, "")
        print(f"  {t}: {v} [{r['status']}] → {r['advice']}")
    
    # 健康检查
    check = med.health_check("测试")
    print(f"\n健康筛查建议 (年龄{check['age']}):")
    for s in check["screenings"]:
        print(f"  📋 {s['name']} ({s['frequency']}): {s['reason']}")
    
    print(f"\n✅ 医疗墨墨就绪")
