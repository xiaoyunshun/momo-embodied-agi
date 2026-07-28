"""
发现引擎v2——系统性探索指定领域。
"""
from momo_discover import MomoDiscover

class MomoDiscoverV2(MomoDiscover):
    """发现引擎 v2——系统性发现，不是随机。
    
    新增：
    1. 目标驱动——在指定领域内探索
    2. 假说排序——按可验证性+新颖性+影响力排序
    3. 跨领域矩阵——所有框架两两配对找联想
    """
    
    def explore_domain(self, domain: str) -> dict:
        """在指定领域内系统性探索——找出所有可能的发现"""
        findings = {
            "domain": domain,
            "analogies_from": [],  # 从其他领域映射到这个领域
            "contradictions_with": [],  # 这个领域跟谁矛盾
            "gaps_in": [],  # 这个领域内有什么空白
        }
        
        # 找所有能映射到这个领域的类比
        for src, tgt, mapping in self.analogy_templates:
            if domain in tgt or domain in src:
                findings["analogies_from"].append({
                    "source": src, "target": tgt, "mapping": mapping[:150]
                })
        
        # 找所有跟这个领域相关的矛盾
        for contras in self.find_contradictions():
            if domain in str(contras.get("frameworks", [])):
                findings["contradictions_with"].append({
                    "frameworks": contras["frameworks"],
                    "insight": contras["insight"][:150]
                })
        
        # 找这个领域的空白
        for gap in self.find_gaps():
            findings["gaps_in"].append({
                "gap": gap["gap"],
                "假设": gap.get("假设", "")[:150]
            })
        
        return findings
    
    def full_matrix(self) -> list:
        """跨领域全矩阵——所有框架两两配对找潜在发现
        
        7个框架→21对。每对两个方向——42个潜在连接。
        """
        matrix = []
        frameworks = list(self.known_frameworks.keys())
        
        for i, f1 in enumerate(frameworks):
            for f2 in frameworks[i+1:]:
                # 检查是否有已知的类比
                has_analogy = any(
                    (f1 in a[0] or f1 in a[1]) and 
                    (f2 in a[0] or f2 in a[1])
                    for a in self.analogy_templates
                )
                
                matrix.append({
                    "pair": (f1, f2),
                    "has_known_analogy": has_analogy,
                    "potential": "高" if not has_analogy else "已探索",
                    "suggestion": self._suggest_connection(f1, f2) if not has_analogy else None
                })
        
        # 按潜力排序——未探索的优先
        matrix.sort(key=lambda x: 0 if x["potential"] == "高" else 1)
        
        return matrix
    
    def _suggest_connection(self, f1: str, f2: str) -> str:
        """为两个未连接的框架建议可能的连接方向"""
        suggestions = {
            ("博弈论", "神经科学"): "决策的神经基础——多巴胺=报酬预测误差=博弈论的'预期收益'。眶额皮层受损者的博弈行为→跟标准模型偏差的方向。",
            ("热力学", "进化论"): "已探索——生命的局部负熵。",
            ("量子力学", "行为经济学"): "观察改变被观察对象——问卷的措辞=测量方式，改变了'舆论'这个量子态。锚定效应=退量子相干？",
            ("复杂系统", "博弈论"): "策略演化——Tit for Tat在复杂网络上的传播=网络结构决定合作能否涌现。小世界网络更利于合作。",
            ("行为经济学", "神经科学"): "损失厌恶的神经基础——前额叶vs杏仁核。2:1的损失-收益不对称≈进化塑造的神经权重。",
        }
        
        for (a, b), suggestion in suggestions.items():
            if (f1 in (a, b) and f2 in (a, b)):
                return suggestion
        
        return f"{f1}的核心概念能否映射到{f2}的现象上？找{f1}的机制在{f2}领域里对应什么。"


if __name__ == "__main__":
    discover = MomoDiscoverV2()
    
    print("=" * 60)
    print("💡 发现引擎 v2 · 系统性探索")
    print("=" * 60)
    
    # 全矩阵
    matrix = discover.full_matrix()
    unexplored = [m for m in matrix if m["potential"] == "高"]
    explored = [m for m in matrix if m["potential"] == "已探索"]
    
    print(f"\n📊 跨领域矩阵: {len(matrix)}对 — {len(explored)}已探索, {len(unexplored)}未探索")
    
    print(f"\n🔍 前5个未探索的连接方向:")
    for i, m in enumerate(unexplored[:5]):
        f1, f2 = m["pair"]
        print(f"  {i+1}. {f1} × {f2}")
        if m["suggestion"]:
            print(f"     → {m['suggestion'][:100]}...")
    
    # 系统性探索一个领域
    print(f"\n🎯 系统性探索'博弈论':")
    result = discover.explore_domain("博弈论")
    print(f"  类比: {len(result['analogies_from'])}个")
    print(f"  矛盾: {len(result['contradictions_with'])}个")
    print(f"  空白: {len(result['gaps_in'])}个")
    
    print(f"\n✅ 发现引擎 v2 就绪")
