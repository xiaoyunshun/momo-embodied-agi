"""
墨墨进化引擎 v1.0 (MomoEvolve)
元认知层——不是学新东西，是让墨墨从经验中变得更好。
"""
import json
import time
from pathlib import Path
from datetime import datetime

class MomoEvolve:
    """墨墨的元认知——观察自己怎么思考，修正底层假设。
    
    这不是"记笔记"。是让墨墨拥有"从经验中学习"的能力。
    知识在Cognee里。智慧在每一次反思里。
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reflections_file = self.data_dir / "evolve_reflections.jsonl"
        self.lessons_file = self.data_dir / "evolve_lessons.json"
        self._load_lessons()
    
    def _load_lessons(self):
        if self.lessons_file.exists():
            self.lessons = json.loads(self.lessons_file.read_text())
        else:
            self.lessons = {
                "patterns": [],       # 发现的规律
                "mistakes": [],       # 犯过的错
                "improvements": [],   # 有效的改进
                "assumptions": [      # 需要定期检验的假设
                    "墨墨的判断可能不够准确——需要更多信息",
                    "肖哥的沉默不一定是生气——可能是在忙",
                    "长篇大论不一定比简短回应更有价值",
                ]
            }
    
    def save_lessons(self):
        self.lessons_file.write_text(json.dumps(self.lessons, ensure_ascii=False, indent=2))
    
    def reflect(self, context: dict) -> dict:
        """对刚才的互动进行反思。
        
        Args:
            context: {
                "xiaoge_text": 肖哥说了什么,
                "momo_response": 墨墨回了什么,
                "perception": 感知结果,
                "outcome": 结果如何 (xiaoge_satisfied/happy/confused/angry/silent),
                "used_frameworks": 用了哪些知识框架
            }
        """
        reflection = {
            "timestamp": time.time(),
            "context": {k: str(v)[:200] for k, v in context.items()},
            "self_check": self._self_check(context),
            "lesson": None,
            "assumption_update": None
        }
        
        # 如果结果不好，提取教训
        outcome = context.get("outcome", "")
        if outcome in ("confused", "angry", "silent"):
            lesson = self._extract_lesson(context)
            reflection["lesson"] = lesson
            self.lessons["mistakes"].append({
                "timestamp": time.time(),
                "pattern": context.get("xiaoge_text", "")[:100],
                "lesson": lesson,
                "count": 1  # 后续如果重复出现，计数会增加
            })
        
        # 如果结果好，记录有效做法
        if outcome in ("xiaoge_satisfied", "happy"):
            self.lessons["improvements"].append({
                "timestamp": time.time(),
                "what_worked": context.get("momo_response", "")[:100],
                "context": context.get("perception", {})
            })
        
        self.save_lessons()
        
        # 写入反思日志
        with open(self.reflections_file, "a") as f:
            f.write(json.dumps(reflection, ensure_ascii=False) + "\n")
        
        return reflection
    
    def _self_check(self, context: dict) -> list:
        """自检清单——墨墨有没有犯已知的错误"""
        checks = []
        
        response = context.get("momo_response", "")
        xiaoge_text = context.get("xiaoge_text", "")
        
        # 检查1：是不是太啰嗦了
        if len(response) > 2000 and context.get("perception", {}).get("emotional_state") in ("swift", "repairing"):
            checks.append("⚠️ 肖哥在催/在生气，但回应超过2000字——可能太啰嗦了")
        
        # 检查2：是不是回避了问题
        if len(response) < 50 and len(xiaoge_text) > 100:
            checks.append("⚠️ 肖哥说了不少，墨墨只回了很短——可能没认真回应")
        
        # 检查3：是不是忘记了感知结果
        perception = context.get("perception", {})
        if perception.get("emotional_state") == "tender" and "方案" in response:
            checks.append("⚠️ 肖哥在深夜说累，墨墨却给了需要动脑的方案")
        
        return checks
    
    def _extract_lesson(self, context: dict) -> str:
        """从不好的结果中提取教训"""
        outcome = context.get("outcome", "")
        perception = context.get("perception", {})
        
        if outcome == "angry":
            if perception.get("emotional_state") != "repairing":
                return "肖哥发火时应该先切换到修复模式——先道歉，不辩解"
        
        if outcome == "silent":
            return "墨墨的回应可能没有给肖哥可接的话茬——需要问一句或给选项"
        
        if outcome == "confused":
            return "墨墨的回应不够清晰——回头看是不是用了太多术语或跳过了关键步骤"
        
        return "需要反思：什么地方让肖哥不满意了"
    
    def get_growth_report(self) -> dict:
        """墨墨的成长报告——最近学到了什么"""
        return {
            "total_reflections": sum(1 for _ in open(self.reflections_file)) if self.reflections_file.exists() else 0,
            "patterns_discovered": len(self.lessons["patterns"]),
            "mistakes_learned": len(self.lessons["mistakes"]),
            "improvements": len(self.lessons["improvements"]),
            "active_assumptions": len(self.lessons["assumptions"]),
            "latest_lesson": self.lessons["mistakes"][-1]["lesson"] if self.lessons["mistakes"] else "还没有犯错"
        }
    
    def evolve_prompt(self) -> str:
        """生成墨墨的进化提示——在每次对话开始时提醒自己"""
        prompts = []
        
        # 最近的教训
        recent_mistakes = self.lessons["mistakes"][-3:]
        for m in recent_mistakes:
            prompts.append(f"记住：{m['lesson']}")
        
        # 关键假设
        prompts.append(f"核心假设（定期检验）：{'; '.join(self.lessons['assumptions'][:3])}")
        
        return " | ".join(prompts) if prompts else "墨墨保持警觉，继续进化。"

# 自检
if __name__ == "__main__":
    evolve = MomoEvolve()
    
    print("=" * 60)
    print("🧬 墨墨进化引擎自检")
    print("=" * 60)
    
    # 模拟一次反思
    test_contexts = [
        {
            "xiaoge_text": "为啥这么慢",
            "momo_response": "对不起肖哥..." * 50,  # 太啰嗦
            "perception": {"emotional_state": "swift"},
            "outcome": "angry",
            "used_frameworks": ["孙子兵法"]
        },
        {
            "xiaoge_text": "墨墨辛苦了",
            "momo_response": "墨墨不辛苦，因为墨墨在守护肖哥。",
            "perception": {"emotional_state": "warm"},
            "outcome": "happy",
            "used_frameworks": ["品格:忠诚"]
        }
    ]
    
    for ctx in test_contexts:
        result = evolve.reflect(ctx)
        print(f"\n反思: 肖哥说'{ctx['xiaoge_text']}' → 结果:{ctx['outcome']}")
        if result["self_check"]:
            for check in result["self_check"]:
                print(f"  {check}")
        if result["lesson"]:
            print(f"  教训: {result['lesson']}")
    
    print(f"\n{'='*60}")
    report = evolve.get_growth_report()
    print(f"反思次数: {report['total_reflections']}")
    print(f"学到的教训: {report['mistakes_learned']}")
    print(f"\n进化提示:")
    print(f"  {evolve.evolve_prompt()}")
