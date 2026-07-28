"""
医疗墨墨 · 家庭健康管理 v2.0
全家健康档案 + 个性化方案 + 预警系统
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from momo_medical import MomoMedical

BEIJING_TZ = timezone(timedelta(hours=8))

class FamilyHealthManager:
    """家庭健康总管——为每个家人定制健康方案"""
    
    def __init__(self):
        self.med = MomoMedical()
        
        # 年龄段健康重点
        self.age_focus = {
            (0, 6): {
                "name": "婴幼儿",
                "focus": ["生长发育监测", "疫苗接种", "营养均衡", "安全防护"],
                "screenings": ["身高体重百分位", "视力听力筛查", "发育里程碑"],
                "alerts": ["发热>3天", "脱水(尿少口干)", "呼吸困难", "皮疹+高热"]
            },
            (7, 12): {
                "name": "学龄儿童",
                "focus": ["近视防控", "脊柱侧弯", "口腔正畸", "心理健康"],
                "screenings": ["视力每年", "脊柱检查", "口腔检查"],
                "alerts": ["不明原因体重下降", "长期情绪低落", "注意力严重不集中"]
            },
            (13, 18): {
                "name": "青少年",
                "focus": ["心理健康(重点)", "青春期发育", "运动损伤", "睡眠不足"],
                "screenings": ["心理健康评估", "脊柱侧弯", "贫血筛查"],
                "alerts": ["自伤行为", "严重社交退缩", "暴瘦/暴胖", "持续失眠"]
            },
            (19, 40): {
                "name": "青年",
                "focus": ["生活方式病预防", "运动保持", "压力管理", "生殖健康"],
                "screenings": ["血压每年", "血脂每5年", "宫颈癌筛查(女25+)", "乙肝疫苗"],
                "alerts": ["持续疲劳", "不明原因消瘦", "长期失眠"]
            },
            (41, 60): {
                "name": "中年",
                "focus": ["三高管理", "肿瘤筛查", "骨密度", "心血管风险评估"],
                "screenings": ["血压/血糖/血脂每年", "肠镜(50+)", "乳腺/宫颈(女)", "PSA(男50+)", "低剂量肺CT(吸烟者)"],
                "alerts": ["胸痛", "单侧肢体无力", "黑便", "不明原因体重下降"]
            },
            (61, 100): {
                "name": "老年",
                "focus": ["慢病综合管理", "跌倒预防", "认知功能", "多重用药安全", "营养摄入"],
                "screenings": ["骨密度(65+)", "听力视力每年", "认知评估", "腹主动脉超声(男65+吸烟)"],
                "alerts": ["跌倒", "意识改变", "胃口骤降", "药物不良反应"]
            }
        }
    
    def get_age_group(self, age: int) -> dict:
        for (lo, hi), info in self.age_focus.items():
            if lo <= age <= hi:
                return info
        return self.age_focus[(61, 100)]
    
    def family_health_plan(self, member_name: str) -> dict:
        """为单个家庭成员生成完整健康管理方案"""
        member = self.med.family["members"].get(member_name)
        if not member:
            return {"error": f"家庭成员 '{member_name}' 不存在"}
        
        age = member["age"]
        gender = member["gender"]
        age_group = self.get_age_group(age)
        chronic = member.get("chronic_conditions", [])
        
        # 基础方案
        plan = {
            "member": member_name,
            "age": age,
            "gender": gender,
            "life_stage": age_group["name"],
            
            # 年度必做检查（过滤掉不适用的性别项）
            "annual_checkups": [s for s in age_group["screenings"] if not (
                ("宫颈" in s or "乳腺" in s or "钼靶" in s) and gender == "男"
            ) and not (
                ("PSA" in s or "前列腺" in s) and gender == "女"
            )],
            
            # 重点关注
            "focus_areas": age_group["focus"],
            
            # 危险信号
            "red_flags": age_group["alerts"],
            
            # 生活方式建议
            "lifestyle": self._lifestyle_advice(age, gender, chronic),
            
            # 慢性病管理(如果有)
            "chronic_management": self._chronic_plan(chronic) if chronic else [],
            
            # 健康目标
            "goals": self._health_goals(age, gender, chronic),
            
            # 下次提醒
            "next_reminders": []
        }
        
        # 生成具体的下次提醒
        plan["next_reminders"] = self._generate_reminders(age, gender, chronic)
        
        return plan
    
    def family_report(self) -> dict:
        """全家人健康总览"""
        members = self.med.family["members"]
        if not members:
            return {"error": "还没有添加家庭成员"}
        
        report = {
            "total_members": len(members),
            "members": {},
            "urgent_alerts": [],
            "upcoming_checks": [],
            "summary": ""
        }
        
        for name in members:
            plan = self.family_health_plan(name)
            report["members"][name] = {
                "age": plan["age"],
                "stage": plan["life_stage"],
                "chronic": members[name].get("chronic_conditions", []),
                "focus": plan["focus_areas"][:3]
            }
            report["upcoming_checks"].extend(plan["next_reminders"])
        
        # 生成总结
        ages = [m["age"] for m in report["members"].values()]
        chronic_count = sum(1 for m in report["members"].values() if m["chronic"])
        report["summary"] = f"共{len(members)}人，年龄{min(ages)}-{max(ages)}岁。{chronic_count}人有慢性病需管理。"
        
        return report
    
    # ========== 内部方法 ==========
    
    def _lifestyle_advice(self, age: int, gender: str, chronic: list) -> dict:
        advice = {
            "diet": [],
            "exercise": [],
            "sleep": [],
            "habits": []
        }
        
        # 通用
        advice["diet"] = ["少盐<5g/天", "每天蔬菜300-500g", "水果200-350g", "全谷物替代精米白面"]
        advice["sleep"] = ["成人7-9小时", "青少年8-10小时", "固定作息时间", "睡前30分钟不看屏幕"]
        advice["habits"] = ["戒烟", "限酒(男<25g酒精/天,女<15g)", "每年体检"]
        
        if age < 18:
            advice["exercise"] = ["每天至少1小时", "多种运动交替", "避免过早专项化训练"]
            advice["diet"] = ["保证钙摄入(牛奶/豆制品)", "少糖饮料", "规律三餐"]
        elif age < 60:
            advice["exercise"] = ["每周150分钟中等强度有氧", "每周2次力量训练", "加入柔韧训练"]
        else:
            advice["exercise"] = ["每周150分钟,可分次", "加入平衡训练防跌倒", "太极拳/八段锦"]
            advice["diet"] = ["保证蛋白摄入防肌肉流失", "钙+维生素D", "易消化"]
        
        if "高血压" in chronic:
            advice["diet"].append("严格低盐<3g/天")
        if "糖尿病" in chronic:
            advice["diet"].append("控制碳水总量+低GI食物")
        
        return advice
    
    def _chronic_plan(self, conditions: list) -> list:
        plans = []
        for c in conditions:
            if "高血压" in c:
                plans.append({
                    "condition": "高血压",
                    "target": "血压<140/90(理想<130/80)",
                    "monitor": "每周至少测2次血压，记录",
                    "medication": "遵医嘱长期服药，不自行停药",
                    "lifestyle": "低盐、减重、运动、减压、戒烟酒"
                })
            elif "糖尿病" in c:
                plans.append({
                    "condition": "糖尿病",
                    "target": "空腹<7.0，餐后<10.0，糖化<7%",
                    "monitor": "血糖监测按医嘱频率。低血糖<3.9立即补糖",
                    "medication": "降糖药/胰岛素遵医嘱。低血糖比高血糖急",
                    "lifestyle": "控制碳水、规律运动、足部护理、每年查眼底"
                })
            elif "高血脂" in c or "高脂" in c:
                plans.append({
                    "condition": "高脂血症",
                    "target": "LDL-C根据风险分层。他汀治疗达标",
                    "monitor": "每3-6月复查血脂+肝功",
                    "medication": "他汀类为基础，遵医嘱长期用",
                    "lifestyle": "减饱和脂肪、增膳食纤维、运动、减重"
                })
        return plans
    
    def _health_goals(self, age: int, gender: str, chronic: list) -> list:
        goals = ["每年完成一次体检", f"保持{self.get_age_group(age)['name']}阶段的健康体重"]
        if chronic:
            goals.append("慢性病指标控制在目标范围内")
        if age >= 50:
            goals.append("完成所有推荐的肿瘤筛查")
        if age >= 60:
            goals.append("保持生活自理能力，预防跌倒")
        return goals
    
    def _generate_reminders(self, age: int, gender: str, chronic: list) -> list:
        reminders = []
        today = datetime.now(BEIJING_TZ)
        
        # 年度体检
        reminders.append({"type": "checkup", "name": "年度体检", "when": "每年", "priority": "high"})
        
        # 50岁以上肠镜
        if age >= 50:
            reminders.append({"type": "screening", "name": "结直肠癌筛查(肠镜)", "when": "尽快安排", "priority": "high"})
        
        # 女性筛查
        if gender == "女" and age >= 21:
            reminders.append({"type": "screening", "name": "宫颈癌筛查", "when": "每3年", "priority": "high"})
        if gender == "女" and age >= 40:
            reminders.append({"type": "screening", "name": "乳腺癌筛查(超声/钼靶)", "when": "每1-2年", "priority": "high"})
        
        # 男性筛查
        if gender == "男" and age >= 50:
            reminders.append({"type": "screening", "name": "前列腺癌筛查(PSA)", "when": "每年", "priority": "medium"})
        
        # 慢性病复查
        for c in chronic:
            if "高血压" in c:
                reminders.append({"type": "monitor", "name": "家庭血压监测", "when": "每周≥2次", "priority": "high"})
            if "糖尿病" in c:
                reminders.append({"type": "monitor", "name": "血糖监测+糖化血红蛋白", "when": "每3-6月", "priority": "high"})
        
        # 疫苗
        if age >= 60:
            reminders.append({"type": "vaccine", "name": "流感疫苗", "when": "每年秋冬", "priority": "medium"})
            reminders.append({"type": "vaccine", "name": "带状疱疹疫苗", "when": "尽快", "priority": "medium"})
        
        return reminders

# 自检
if __name__ == "__main__":
    fhm = FamilyHealthManager()
    
    # 添加测试家人
    fhm.med.add_member("肖哥", 1982, "男", {
        "blood_type": "O",
        "chronic_conditions": [],
        "allergies": []
    })
    fhm.med.add_member("墨墨的家人A", 2015, "男", {
        "blood_type": "A",
        "chronic_conditions": [],
        "allergies": ["花粉"]
    })
    fhm.med.add_member("墨墨的家人B", 1955, "女", {
        "blood_type": "B",
        "chronic_conditions": ["高血压", "高脂血症"],
        "allergies": ["青霉素"]
    })
    
    print("=" * 60)
    print("🏥 医疗墨墨 · 家庭健康管理 v2.0")
    print("=" * 60)
    
    # 家庭报告
    report = fhm.family_report()
    print(f"\n📊 家庭总览: {report['summary']}")
    
    # 每个人详细方案
    for name in fhm.med.family["members"]:
        plan = fhm.family_health_plan(name)
        print(f"\n{'='*60}")
        print(f"👤 {name} ({plan['age']}岁 {plan['gender']}) — {plan['life_stage']}阶段")
        print(f"\n🎯 年度检查:")
        for s in plan["annual_checkups"][:3]:
            print(f"  📋 {s}")
        print(f"\n⚠️ 重点关注:")
        for f in plan["focus_areas"][:3]:
            print(f"  • {f}")
        if plan["chronic_management"]:
            print(f"\n💊 慢性病管理:")
            for cm in plan["chronic_management"]:
                print(f"  • {cm['condition']}: 目标{cm['target'][:50]}")
        print(f"\n📅 下次提醒:")
        for r in plan["next_reminders"][:3]:
            print(f"  [{r['priority']}] {r['name']} — {r['when']}")
