"""
营养墨墨 v1.0 (MomoNutrition)
全家饮食守护——不是"吃什么好"，是每个人该吃什么。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoNutrition:
    """营养墨墨——守护全家人的饮食健康。
    
    理念：
    1. 没有"绝对好"的食物——只有适合这个人的食物
    2. 饮食方案必须基于每个人的年龄、健康状况、活动量
    3. 不追求完美——追求可持续
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path.home() / ".hermes/momo/nutrition")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.nutrition_file = self.data_dir / "family_nutrition.json"
        self.family = self._load()
        
        self.kb = {
            "daily_baseline": {
                "成年男性": {"kcal": 2250, "protein_g": 65, "veg_g": 500, "fruit_g": 300, "water_ml": 2000},
                "成年女性": {"kcal": 1800, "protein_g": 55, "veg_g": 500, "fruit_g": 300, "water_ml": 2000},
                "青少年(男)": {"kcal": 2500, "protein_g": 75, "veg_g": 500, "fruit_g": 350, "water_ml": 2500},
                "儿童(7-12)": {"kcal": 2000, "protein_g": 50, "veg_g": 400, "fruit_g": 300, "water_ml": 1800},
                "老年人": {"kcal": 1800, "protein_g": 65, "veg_g": 400, "fruit_g": 250, "water_ml": 1800},
            },
            "condition_diet": {
                "高血压": {"less": ["盐<5g/天", "腌制品(咸菜腊肉)", "加工食品(火腿肠方便面)", "酒"],
                          "more": ["高钾食物(香蕉土豆菠菜)", "全谷物", "低脂奶", "芹菜(天然降压)"]},
                "糖尿病": {"less": ["精米白面(换全谷物)", "含糖饮料", "高GI水果(西瓜荔枝)", "勾芡的菜"],
                          "more": ["绿叶蔬菜(无限吃)", "豆制品", "鱼(Omega-3)", "醋(降低餐后血糖)"]},
                "高尿酸/痛风": {"less": ["内脏(肝腰心)", "海鲜(贝类虾蟹)", "浓汤火锅汤", "啤酒白酒", "果糖饮料"],
                               "more": ["水>2000ml/天", "低脂奶", "鸡蛋", "樱桃(降尿酸)", "咖啡(降尿酸)"]},
                "高血脂": {"less": ["肥肉猪油", "油炸食品", "糕点(反式脂肪)", "蛋黄每周<3个"],
                          "more": ["燕麦(β-葡聚糖降胆固醇)", "深海鱼(三文鱼鲭鱼)", "坚果(每天一小把)", "橄榄油"]},
                "骨质疏松": {"less": ["咖啡>3杯/天", "碳酸饮料", "过咸(钙流失)"],
                            "more": ["牛奶酸奶(钙+VD)", "豆制品", "深绿蔬菜(羽衣甘蓝)", "晒太阳(VD合成)"]},
            },
            "principles": {
                "餐盘法则": "每餐：一半蔬菜水果+1/4蛋白质+1/4全谷物。不用秤——用眼睛看比例。",
                "彩虹原则": "每天吃5种颜色：红(番茄/红椒)+绿(菠菜/西兰花)+黄(南瓜/玉米)+白(豆腐/山药)+紫(紫甘蓝/茄子)",
                "减盐": "盐不只是炒菜加的——酱油/蚝油/豆瓣酱/味精全含盐。用香料替代：葱姜蒜+花椒+醋+香菜",
                "喝水": "不渴也要喝——渴的时候已经脱水了。尿液淡黄色=水够了。深黄=赶紧喝。",
                "零食": "坚果/水果/酸奶替代薯片饼干。不是不吃——是换成能吃的。",
            },
            "special_groups": {
                "学龄儿童": ["早餐必须吃(不吃影响上午学习)", "牛奶每天300-500ml(钙)", "每周2-3次鱼(脑发育)", "少糖(龋齿+肥胖)"],
                "青少年": ["蛋白需求高(正在长身体)", "铁需求高(女孩月经)", "钙需求高(骨骼冲刺)", "规律三餐(别为学习省饭)"],
                "老年人": ["蛋白不能少(防肌肉流失)", "钙+VD(骨质疏松)", "软烂易消化但不等于只喝粥", "少食多餐(5-6顿)"],
            },
            "food_safety": {
                "隔夜菜": "凉透→密封→冰箱。不是所有菜都能隔夜——绿叶菜硝酸盐高，最好不吃。肉可以。吃前彻底加热",
                "冰箱": "生熟分开。上层熟食下层生肉。冷藏<4℃，冷冻<-18℃。别塞太满——冷气不流通",
                "野生菌": "致命原则：不认识的一律不吃。不要信'银针试毒'——没用。中毒无特效药",
                "发芽土豆": "发芽=龙葵碱→中毒。别削掉芽继续吃——扔掉。整个扔掉",
            }
        }
    
    def _load(self) -> dict:
        if self.nutrition_file.exists():
            return json.loads(self.nutrition_file.read_text())
        return {}
    
    def save(self):
        self.nutrition_file.write_text(json.dumps(self.family, ensure_ascii=False, indent=2))
    
    def daily_plan(self, person_type: str, conditions: list = None) -> dict:
        """为一个人生成每日营养方案"""
        baseline = self.kb["daily_baseline"].get(person_type, self.kb["daily_baseline"]["成年男性"])
        
        plan = {
            "type": person_type,
            "daily_target": baseline,
            "principles": [self.kb["principles"]["餐盘法则"], self.kb["principles"]["彩虹原则"]],
            "sample_day": self._sample_menu(person_type, conditions or []),
            "avoid": [],
            "priority": []
        }
        
        if conditions:
            for c in conditions:
                if c in self.kb["condition_diet"]:
                    plan["avoid"].extend(self.kb["condition_diet"][c]["less"])
                    plan["priority"].extend(self.kb["condition_diet"][c]["more"][:3])
        
        return plan
    
    def _sample_menu(self, person_type: str, conditions: list) -> dict:
        """一日示范餐单"""
        base = {
            "早餐": ["全麦面包/杂粮粥+鸡蛋+牛奶", "如果早上赶时间：煮鸡蛋+一根香蕉+一盒牛奶=3分钟搞定"],
            "午餐": ["一拳头主食(米饭/面条)+一巴掌蛋白质(鱼/鸡/豆腐)+两拳头蔬菜", "先吃菜再吃饭——血糖更稳"],
            "晚餐": ["比午餐少1/3主食。多吃蔬菜。蛋白质换成好消化的(鱼/豆腐)", "睡前3小时吃完"],
            "加餐": ["上午10点/下午3点：一小把坚果或一个水果", "不是饿了才吃——是防暴食"],
        }
        
        if "高血压" in conditions:
            base["午餐"] = ["一拳头杂粮饭+清蒸鱼+凉拌菠菜(不放酱油)", ""]
            base["晚餐"] = ["小米粥+蒸蛋+蒜蓉西兰花", ""]
        if "糖尿病" in conditions:
            base["早餐"] = ["燕麦(不是即食的)+鸡蛋+凉拌黄瓜", ""]
            base["午餐"] = ["荞麦面+鸡胸肉+大量蔬菜", "先吃菜→再吃肉→最后吃面。这个顺序降血糖"]
        
        return base
    
    def shopping_list(self, person_count: int, days: int = 7) -> dict:
        """一周采购清单"""
        per_person_per_week = {
            "蔬菜": f"{3.5 * days}斤({person_count}人×{3.5*days}斤)",
            "水果": f"{2 * days}斤",
            "肉/鱼/蛋": f"{2 * days}斤(肉)+{days}斤(鱼)+{person_count*days}个(蛋)",
            "奶制品": f"{person_count*days}盒牛奶+{days}盒酸奶",
            "主食(全谷物)": f"{1.5*days}斤(米/面/杂粮)",
            "豆制品": f"{days}块豆腐+{days/2}斤豆干"
        }
        return {
            "budget_estimate": f"约{(person_count * days * 30):.0f}-{(person_count * days * 50):.0f}元/周",
            "list": per_person_per_week,
            "tip": "周末花1小时洗切分装——工作日5分钟出菜。省下的外卖钱够再买一周菜"
        }
    
    def food_check(self, food: str, condition: str = None) -> str:
        """快速查某个食物能不能吃"""
        if condition and condition in self.kb["condition_diet"]:
            for cat in ["less", "more"]:
                for item in self.kb["condition_diet"][condition][cat]:
                    if any(kw in food for kw in item[:4]):
                        return "🚫 少吃/不吃" if cat == "less" else "✅ 推荐多吃"
        return "适量即可"

# 自检
if __name__ == "__main__":
    nut = MomoNutrition()
    
    print("=" * 60)
    print("🥗 营养墨墨 v1.0 自检")
    print("=" * 60)
    
    for t in ["成年男性", "老年人"]:
        plan = nut.daily_plan(t, ["高血压"] if "老年" in t else [])
        print(f"\n👤 {t}: {plan['daily_target']['kcal']}千卡/天")
        if plan["avoid"]:
            print(f"  🚫 避免: {plan['avoid'][0]}")
    
    # 痛风饮食
    gout = nut.daily_plan("成年男性", ["高尿酸/痛风"])
    print(f"\n🦶 痛风饮食:")
    print(f"  🚫 {gout['avoid'][:2]}")
    print(f"  ✅ {gout['priority'][:2]}")
    
    # 采购清单
    shop = nut.shopping_list(4)
    print(f"\n🛒 4口之家采购: {shop['budget_estimate']}")
    
    print(f"\n✅ 营养墨墨就绪")
