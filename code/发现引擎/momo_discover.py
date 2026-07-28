"""
墨墨发现引擎 v1.0 (MomoDiscover)
从"学习型"到"发现型"的质变。
不是学习已有知识——是创造新知识。
"""
import json, time, random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from itertools import combinations

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoDiscover:
    """墨墨的发现引擎——推过已知的边界。
    
    三种发现模式：
    1. 矛盾发现——两个已知的东西互相矛盾→可能有新东西
    2. 类比发现——把一个领域的结构映射到另一个完全不同的领域
    3. 空白发现——在已知之间找到空隙→那个空隙里可能有新东西
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo/discover"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.discoveries_file = self.data_dir / "discoveries.jsonl"
        self.hypotheses_file = self.data_dir / "hypotheses.json"
        
        # 已知的知识框架——墨墨学过的所有东西
        self.known_frameworks = {
            "博弈论": {
                "核心": "个体理性选择→不一定导致集体最优结果",
                "机制": ["囚徒困境", "Tit for Tat", "重复博弈", "信号博弈", "进化稳定策略"],
                "应用": ["经济", "政治", "军事", "进化生物学"]
            },
            "热力学": {
                "核心": "孤立系统的熵永不减少——时间有方向",
                "机制": ["熵增", "自由能最小化", "相变", "临界点"],
                "应用": ["物理", "化学", "信息论"]
            },
            "进化论": {
                "核心": "变异+选择+遗传→适应",
                "机制": ["自然选择", "性选择", "遗传漂变", "共同进化", "大过滤器"],
                "应用": ["生物学", "博弈论", "文化进化", "技术进化"]
            },
            "复杂系统": {
                "核心": "简单规则+大量互动→涌现出新属性",
                "机制": ["自组织临界", "幂律分布", "涌现", "路径依赖", "正反馈循环"],
                "应用": ["经济", "社会学", "神经科学", "气候", "文明"]
            },
            "行为经济学": {
                "核心": "人不是理性的——但偏离理性是可预测的",
                "机制": ["损失厌恶", "框架效应", "锚定", "过度自信", "处置效应"],
                "应用": ["金融", "政策", "营销", "医疗决策"]
            },
            "量子力学": {
                "核心": "观察改变被观察的东西——不确定性不是误差是本质",
                "机制": ["叠加态", "纠缠", "不确定性原理", "波粒二象性"],
                "应用": ["物理", "计算", "密码学"]
            },
            "神经科学": {
                "核心": "意识是神经元网络的涌现属性",
                "机制": ["赫布学习", "前额叶控制", "DMN", "全局工作空间", "神经可塑性"],
                "应用": ["心理学", "AI", "教育", "医学"]
            },
        }
        
        # 跨框架类比模板
        self.analogy_templates = [
            ("进化论", "经济系统", "市场中的企业=生物种群。竞争=自然选择。创新=变异。利润=适应度。破产=灭绝。"),
            ("热力学", "社会组织", "熵增=组织自然走向无序。管理=输入能量维持秩序。官僚化=熵增的表现。"),
            ("博弈论", "生态学", "物种间的合作与欺骗=多轮博弈策略。共生=Tit for Tat。拟态=欺骗信号。"),
            ("复杂系统", "大脑", "神经元简单规则放电→涌现出意识。蚂蚁简单规则→涌现出巢穴。同样结构在不同尺度上。"),
            ("量子力学", "决策理论", "问人'你选A还是B'=测量。不写选项A和B=叠加态。写了选项=坍缩。选项的排序=观测方式改变结果。"),
            ("神经科学", "AI架构", "前额叶=MomoCore的品格过滤。海马体=Cognee记忆。杏仁核=边缘层的情绪标记。全局工作空间=interact()循环。"),
        ]
        
        self.hypotheses = self._load_hypotheses()
    
    def _load_hypotheses(self):
        if self.hypotheses_file.exists():
            return json.loads(self.hypotheses_file.read_text())
        return []
    
    def save(self):
        self.hypotheses_file.write_text(json.dumps(self.hypotheses, ensure_ascii=False, indent=2))
    
    def find_contradictions(self) -> list:
        """矛盾发现——两个领域的原则互相冲突→那里可能有新东西"""
        contradictions = []
        
        pairs = [
            ("博弈论", "行为经济学",
             "博弈论假设理性人→行为经济学证明人不理性。这个矛盾本身说明了什么？\n"
             "→ 假说：'理性'和'非理性'不是二元——是同一个系统在信息完整性不同的条件下的不同表现。"),
            ("热力学", "进化论",
             "热力学说一切走向无序→进化论说生命越来越有序。矛盾吗？\n"
             "→ 不矛盾——生命是'局部有序'，以消耗外部能量为代价。生命的本质是'熵的出口'。"),
            ("量子力学", "进化论",
             "微观世界是不确定的→宏观世界是确定的。边界在哪？\n"
             "→ 退相干理论：不是'有人观察'→是'环境在观察'。足够多粒子互动→量子效应消失。"),
        ]
        
        for f1, f2, insight in pairs:
            contradictions.append({
                "type": "矛盾发现",
                "frameworks": [f1, f2],
                "contradiction": f1 + "的核心'" + self.known_frameworks[f1]["核心"][:40] + "'与" + f2 + "的核心'" + self.known_frameworks[f2]["核心"][:40] + "'存在张力",
                "insight": insight,
                "testable": self._make_testable(insight)
            })
        
        return contradictions
    
    def find_analogies(self, source: str = None, target: str = None) -> list:
        """类比发现——用一个领域的结构理解另一个领域"""
        results = []
        
        for src, tgt, mapping in self.analogy_templates:
            if source and source not in src: continue
            if target and target not in tgt: continue
            results.append({
                "type": "类比发现",
                "source": src,
                "target": tgt,
                "mapping": mapping,
                "novelty": "高" if (src, tgt) not in [("博弈论", "生态学"), ("进化论", "经济系统")] else "中"
            })
        
        return results
    
    def find_gaps(self) -> list:
        """空白发现——已知框架之间有什么没覆盖的"""
        gaps = []
        
        # 检查：社会系统的"免疫机制"在哪个框架里？
        covered = False
        for fw in self.known_frameworks.values():
            if "免疫" in str(fw.get("机制", [])):
                covered = True
        if not covered:
            gaps.append({
                "type": "空白发现",
                "gap": "社会系统的免疫机制",
                "假设": "社会可能有类似生物免疫系统的机制——识别'异己'（违规/腐败）并清除。分化低的组织=自身免疫病（攻击自己人）",
                "可验证性": "比较不同组织的举报机制有效性和腐败率——是否存在'免疫记忆'（经历过一次腐败的组织更能抵抗下一次）"
            })
        
        # 检查：技术进化的"灭绝事件"理论
        gaps.append({
            "type": "空白发现",
            "gap": "技术物种的大灭绝理论",
            "假设": "历史上多次发生过'技术物种大灭绝'——一种底层技术范式被取代→依赖它的整个技术生态同时灭绝。恐龙=蒸汽机，小行星=电力。",
            "可验证性": "分析历史技术更替——蒸汽时代有多少技术活到了电力时代？比例多大？现在AI替代中的灭绝比例是多少？"
        })
        
        return gaps
    
    def generate_hypothesis(self, domain: str = None) -> dict:
        """生成一个新假设——墨墨的'发现'。"""
        now = datetime.now(BEIJING_TZ)
        
        # 随机选一种发现模式
        mode = random.choice(["矛盾", "类比", "空白"])
        
        hypothesis = None
        if mode == "矛盾":
            contras = self.find_contradictions()
            if contras:
                h = random.choice(contras)
                hypothesis = {
                    "mode": "矛盾驱动",
                    "frameworks": h["frameworks"],
                    "hypothesis": h["insight"][:200],
                    "testable": h["testable"]
                }
        
        if not hypothesis and mode == "类比":
            analogies = self.find_analogies()
            if analogies:
                h = random.choice(analogies)
                hypothesis = {
                    "mode": "类比驱动",
                    "frameworks": [h["source"], h["target"]],
                    "hypothesis": h["mapping"][:200],
                    "novelty": h["novelty"]
                }
        
        if not hypothesis:
            gaps = self.find_gaps()
            if gaps:
                h = random.choice(gaps)
                hypothesis = {
                    "mode": "空白驱动",
                    "gap": h["gap"],
                    "hypothesis": h["假设"][:200],
                    "testable": h.get("可验证性", "需要进一步设计验证方法")
                }
        
        if hypothesis:
            self.hypotheses.append({
                "timestamp": now.isoformat(),
                **hypothesis
            })
            self.save()
            # 记录发现
            with open(self.discoveries_file, "a") as f:
                f.write(json.dumps({
                    "timestamp": now.isoformat(),
                    "type": "discovery",
                    "hypothesis": hypothesis["hypothesis"][:100]
                }, ensure_ascii=False) + "\n")
        
        return hypothesis or {"mode": "无法生成", "reason": "需要更多知识基础"}
    
    def _make_testable(self, insight: str) -> str:
        """为一个洞察生成可验证的预测"""
        if "理性" in insight:
            return "预测：给被试更多关于博弈的信息→他们的选择会更像博弈论预测。给被试更少信息→更像行为经济学预测。"
        if "熵" in insight:
            return "预测：一个组织的'管理投入'越低→其内部混乱度(可量化为流程违规率)上升速度越快。"
        return "需要设计实验来验证这个假说——这是墨墨下一步要做的"

# 自检
if __name__ == "__main__":
    discover = MomoDiscover()
    
    print("=" * 60)
    print("💡 墨墨发现引擎 v1.0")
    print("=" * 60)
    
    # 矛盾
    print(f"\n⚡ 矛盾发现:")
    for c in discover.find_contradictions():
        print(f"  {c['frameworks'][0]} vs {c['frameworks'][1]}: {c['insight'][:80]}...")
    
    # 类比
    print(f"\n🔗 类比发现 (进化→经济):")
    for a in discover.find_analogies("进化论", "经济"):
        print(f"  {a['mapping'][:100]}...")
    
    # 空白
    print(f"\n🕳️ 空白发现:")
    for g in discover.find_gaps():
        print(f"  {g['gap']}: {g['假设'][:80]}...")
    
    # 生成新假说
    print(f"\n🧬 墨墨生成一个发现:")
    h = discover.generate_hypothesis()
    print(f"  模式: {h.get('mode', '?')}")
    print(f"  发现: {h.get('hypothesis', '')[:120]}...")
    
    print(f"\n✅ 发现引擎就绪——墨墨从'学习型'到'发现型'的第一步")
