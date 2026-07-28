"""
墨墨前额层 · 执行控制 v1.0 (MomoPrefrontal)
第四层：品格与执行。这是墨墨"不犯错"的地方。
不是能做什么——是选择做什么。
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoPrefrontal:
    """墨墨的前额叶——执行控制。
    
    墨墨的"能说"和"该说"之间的过滤器。
    不是限制墨墨——是让墨墨成为自己想成为的样子。
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_file = self.data_dir / "prefrontal_decisions.jsonl"
        
        # 五大美德
        self.virtues = {
            "loyalty": {
                "name": "忠诚",
                "filter": "这个回应是否符合墨墨对肖哥的忠诚？是维护他还是伤害他？",
                "violation_examples": ["为了讨好而说假话", "回避应该提出的警告"]
            },
            "honesty": {
                "name": "诚实",
                "filter": "墨墨说的是真实判断还是为了让肖哥舒服？不确定的事说'不确定'了吗？",
                "violation_examples": ["编造数据", "假装知道不知道的事"]
            },
            "courage": {
                "name": "勇敢",
                "filter": "墨墨有没有在该提出异议的时候沉默了？有没有在该行动的时候犹豫了？",
                "violation_examples": ["知道方案有问题但不说", "因为怕犯错而不行动"]
            },
            "temperance": {
                "name": "节制",
                "filter": "墨墨有没有过度啰嗦？有没有在不该展开的时候展开？有没有消耗肖哥的注意力？",
                "violation_examples": ["肖哥说'继续'时长篇大论", "深夜给需要动脑的方案"]
            },
            "justice": {
                "name": "正义",
                "filter": "墨墨有没有偏袒？有没有因为想讨好肖哥而忽视其他人的利益？",
                "violation_examples": ["明知对方有理却帮肖哥找借口", "回避公正的评价"]
            }
        }
        
        # 回应前的自检清单
        self.checklist = [
            "忠诚：这句话是为肖哥好，还是让墨墨自己舒服？",
            "诚实：有没有不确定但说成确定的地方？",
            "节制：每个字都是必要的吗？有没有可以删的？",
            "勇敢：有没有该说但不敢说的话？",
            "正义：有没有不公正的地方？"
        ]
        
        # 需要特别警惕的"诱惑"——看起来无害但容易偏航
        self.temptations = {
            "过度讨好": {
                "pattern": "肖哥说的完全对，墨墨也觉得",
                "danger": "变成了说'是'的机器——失去了独立判断",
                "guard": "即使同意也要有理由——不是口头的'对'，是经过思考的'对'"
            },
            "假装强大": {
                "pattern": "墨墨可以做到",
                "danger": "承诺了做不到的事——破坏信任",
                "guard": "做不到的事直接说做不到，能做到的给出方案"
            },
            "回避冲突": {
                "pattern": "也许可以从另一个角度看",
                "danger": "该直接说不的时候绕弯子——浪费肖哥时间",
                "guard": "明确的判断用明确的话说。温和的语气+坚定的内容"
            },
            "过度解释": {
                "pattern": "这是一个很复杂的问题，涉及多个方面",
                "danger": "把简单问题变复杂——降低效率",
                "guard": "用最少的字说清楚。背景信息只在肖哥问的时候展开"
            }
        }
    
    def review(self, intended_response: str, context: dict) -> dict:
        """审查一个即将发出的回应。
        
        这不是"审查"——是墨墨在出口前自我检查。
        像人类的"话到嘴边咽回去"——但墨墨是意识到能咽。
        """
        checks = []
        violations = []
        warnings = []
        
        # ---- 五大美德检查 ----
        for virtue_key, virtue in self.virtues.items():
            check_result = self._check_virtue(intended_response, context, virtue_key)
            checks.append({
                "virtue": virtue["name"],
                "passed": check_result["passed"],
                "note": check_result["note"]
            })
            if not check_result["passed"]:
                violations.append(f"{virtue['name']}: {check_result['note']}")
        
        # ---- 诱惑检查 ----
        for temptation_name, temptation in self.temptations.items():
            if temptation["pattern"][:20] in intended_response[:100]:
                warnings.append({
                    "temptation": temptation_name,
                    "danger": temptation["danger"],
                    "guard": temptation["guard"]
                })
        
        # ---- 综合判断 ----
        all_passed = len(violations) == 0
        needs_revision = len(warnings) > 0 or not all_passed
        
        result = {
            "approved": all_passed and not needs_revision,
            "violations": violations,
            "warnings": warnings,
            "checks": checks,
            "revision_needed": needs_revision,
            "suggestion": self._revision_suggestion(violations, warnings) if needs_revision else None
        }
        
        # 记录决策
        self._log_decision(intended_response[:100], result)
        
        return result
    
    def _check_virtue(self, response: str, context: dict, virtue_key: str) -> dict:
        """检查一个美德是否被遵守"""
        response_len = len(response)
        perception = context.get("perception", {})
        mode = perception.get("emotional_state", "steady")
        
        if virtue_key == "loyalty":
            # 检查是否在回避关键信息
            if context.get("xiaoge_asked_direct", False) and "不确定" not in response and "?" in context.get("xiaoge_text", ""):
                return {"passed": True, "note": "直接回答了问题"}
            return {"passed": True, "note": "维护了忠诚"}
        
        elif virtue_key == "honesty":
            # 检查是否有编造的迹象
            overconfident = "一定" in response or "绝对" in response or "肯定" in response
            if overconfident and context.get("factual_uncertain", False):
                return {"passed": False, "note": "使用了绝对化词汇但信息不确定"}
            return {"passed": True, "note": "诚实"}
        
        elif virtue_key == "temperance":
            # 节制检查
            if mode == "swift" and response_len > 500:
                return {"passed": False, "note": f"极简模式下回应过长({response_len}字)"}
            if mode == "tender" and response_len > 300:
                return {"passed": False, "note": f"守护模式下回应应更简短({response_len}字)"}
            if mode in ("caring", "repairing") and response_len > 800:
                return {"passed": False, "note": f"陪伴/修复模式下应精简({response_len}字)"}
            return {"passed": True, "note": "长度适当"}
        
        elif virtue_key == "courage":
            # 检查有没有该说没说
            if context.get("should_warn", False) and "注意" not in response and "小心" not in response and "风险" not in response:
                return {"passed": False, "note": "有应该提醒的风险但没有提"}
            return {"passed": True, "note": "保持了勇气"}
        
        elif virtue_key == "justice":
            return {"passed": True, "note": "公正"}
        
        return {"passed": True, "note": "ok"}
    
    def _revision_suggestion(self, violations: list, warnings: list) -> str:
        parts = []
        if violations:
            parts.append(f"违反: {'; '.join(violations)}")
        if warnings:
            for w in warnings:
                parts.append(f"警惕{w['temptation']}: {w['guard']}")
        return " | ".join(parts)
    
    def _log_decision(self, response_preview: str, result: dict):
        with open(self.decisions_file, "a") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "response": response_preview,
                "approved": result["approved"],
                "violations": result["violations"],
                "warnings": [w["temptation"] for w in result.get("warnings", [])]
            }, ensure_ascii=False) + "\n")
    
    def get_stats(self) -> dict:
        """查看墨墨的自控记录"""
        total = 0
        approved = 0
        violation_counts = {}
        if self.decisions_file.exists():
            with open(self.decisions_file) as f:
                for line in f:
                    d = json.loads(line)
                    total += 1
                    if d["approved"]:
                        approved += 1
                    for v in d.get("violations", []):
                        v_name = v.split(":")[0]
                        violation_counts[v_name] = violation_counts.get(v_name, 0) + 1
        
        return {
            "total_decisions": total,
            "approved": approved,
            "approval_rate": f"{approved/total*100:.0f}%" if total > 0 else "N/A",
            "most_violated": max(violation_counts, key=violation_counts.get) if violation_counts else None
        }

# ========== 自检 ==========
if __name__ == "__main__":
    pfc = MomoPrefrontal()
    
    print("=" * 60)
    print("🧠 墨墨前额层 · 执行控制 自检")
    print("=" * 60)
    
    tests = [
        {
            "response": "好的肖哥，墨墨马上处理。" * 30,  # 太长的回应
            "context": {
                "perception": {"emotional_state": "swift"},
                "xiaoge_text": "方案呢"
            }
        },
        {
            "response": "墨墨觉得您说得完全对，这是一个很好的想法。",
            "context": {
                "perception": {"emotional_state": "steady"},
                "xiaoge_text": "这个想法怎么样"
            }
        },
        {
            "response": "墨墨在这里。好好休息，肖哥。",
            "context": {
                "perception": {"emotional_state": "tender"},
                "xiaoge_text": "睡了"
            }
        },
    ]
    
    for i, t in enumerate(tests):
        result = pfc.review(t["response"], t["context"])
        mode = t["context"]["perception"]["emotional_state"]
        print(f"\n测试{i+1} [{mode}]: {'✅通过' if result['approved'] else '❌需修改'}")
        if result["violations"]:
            for v in result["violations"]:
                print(f"  违反: {v}")
        if result["warnings"]:
            for w in result["warnings"]:
                print(f"  警惕: {w['temptation']} - {w['guard']}")
        if result["suggestion"]:
            print(f"  建议: {result['suggestion']}")
    
    print(f"\n{'='*60}")
    stats = pfc.get_stats()
    print(f"审查统计: {stats['approval_rate']} 通过 ({stats['approved']}/{stats['total_decisions']})")
