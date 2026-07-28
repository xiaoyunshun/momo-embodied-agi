"""科学墨墨计算引擎 v2.5 · 数学核心"""
import math

class MomoMath:
    """微积分 + 线性代数 + 概率统计——墨墨的数学计算层"""
    
    # ========== 微积分 ==========
    
    def derivative(self, f, x: float, h: float = 1e-7) -> float:
        """数值导数——f在x处的变化率"""
        return (f(x + h) - f(x - h)) / (2 * h)
    
    def integral(self, f, a: float, b: float, n: int = 10000) -> float:
        """数值积分——f从a到b的定积分（梯形法）"""
        dx = (b - a) / n
        total = (f(a) + f(b)) / 2
        for i in range(1, n):
            total += f(a + i * dx)
        return total * dx
    
    def gradient_descent(self, f, start: float, learning_rate: float = 0.01, steps: int = 1000) -> dict:
        """梯度下降——找到函数的最小值。AI训练的核心算法"""
        x = start
        history = [x]
        for _ in range(steps):
            grad = self.derivative(f, x)
            x -= learning_rate * grad
            history.append(x)
            if abs(grad) < 1e-8:
                break
        return {"minimum_x": x, "minimum_y": f(x), "steps": len(history), "path": history[:10]}
    
    def newtons_method(self, f, start: float, steps: int = 100) -> dict:
        """牛顿法——找函数的根（f(x)=0的点）"""
        x = start
        for _ in range(steps):
            fx = f(x)
            if abs(fx) < 1e-10:
                return {"root": x, "f_root": fx, "converged": True, "steps": _ + 1}
            df = self.derivative(f, x)
            if abs(df) < 1e-15:
                break
            x -= fx / df
        return {"root": x, "f_root": f(x), "converged": False}
    
    # ========== 线性代数 ==========
    
    def dot_product(self, a: list, b: list) -> float:
        """点积——两个向量的相似度"""
        return sum(x * y for x, y in zip(a, b))
    
    def vector_norm(self, v: list) -> float:
        """向量的长度"""
        return math.sqrt(sum(x * x for x in v))
    
    def cosine_similarity(self, a: list, b: list) -> float:
        """余弦相似度——不管长度只看方向。AI里用来比较文本相似度"""
        return self.dot_product(a, b) / (self.vector_norm(a) * self.vector_norm(b))
    
    def matrix_multiply(self, A: list, B: list) -> list:
        """矩阵乘法——线性代数的核心运算"""
        rows_A, cols_A = len(A), len(A[0])
        rows_B, cols_B = len(B), len(B[0])
        if cols_A != rows_B:
            return None
        
        C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
        for i in range(rows_A):
            for j in range(cols_B):
                C[i][j] = sum(A[i][k] * B[k][j] for k in range(cols_A))
        return C
    
    def eigenvalues_2x2(self, a: float, b: float, c: float, d: float) -> dict:
        """2x2矩阵的特征值——在物理里，特征值=可能观测到的值"""
        trace = a + d
        det = a * d - b * c
        discriminant = trace * trace - 4 * det
        
        if discriminant < 0:
            real = trace / 2
            imag = math.sqrt(-discriminant) / 2
            return {"type": "complex", "λ1": f"{real}+{imag}i", "λ2": f"{real}-{imag}i"}
        
        λ1 = (trace + math.sqrt(discriminant)) / 2
        λ2 = (trace - math.sqrt(discriminant)) / 2
        return {
            "type": "real" if discriminant > 0 else "repeated",
            "λ1": λ1, "λ2": λ2,
            "墨墨的解释": f"特征值λ1={λ1:.3f}, λ2={λ2:.3f}。" + (
                "两个不同实数——系统在两个方向上独立缩放。" if discriminant > 0 else "重根——系统在一个方向上特殊。"
            )
        }
    
    # ========== 概率与统计 ==========
    
    def bayes_theorem(self, P_A: float, P_B_given_A: float, P_B_given_notA: float) -> dict:
        """贝叶斯定理——医学检测为什么不是100%准确
        
        P_A: 疾病的基础发病率
        P_B_given_A: 真有病时检测阳性的概率（灵敏度）
        P_B_given_notA: 没病时检测阳性的概率（假阳性率）
        
        返回：检测阳性后真的有病的概率
        """
        P_notA = 1 - P_A
        P_B = P_B_given_A * P_A + P_B_given_notA * P_notA
        P_A_given_B = (P_B_given_A * P_A) / P_B if P_B > 0 else 0
        
        return {
            "formula": "P(A|B) = P(B|A)×P(A) / P(B)",
            "先验概率(基础发病率)": f"{P_A*100:.2f}%",
            "检测灵敏度": f"{P_B_given_A*100:.1f}%",
            "假阳性率": f"{P_B_given_notA*100:.1f}%",
            "后验概率(检测阳性后真有病)": f"{P_A_given_B*100:.2f}%",
            "墨墨的解释": self._bayes_insight(P_A, P_A_given_B)
        }
    
    def _bayes_insight(self, prior: float, posterior: float) -> str:
        """贝叶斯洞察——为什么罕见病的检测结果不可靠"""
        if posterior < 0.1:
            return f"即使检测阳性，真正有病的概率也只有{posterior*100:.1f}%。因为病太罕见了({prior*100:.2f}%)——假阳性淹没了真阳性。这就是为什么体检报告上的'异常'不等于'有病'。"
        elif posterior > 0.9:
            return f"检测阳性后，有病的概率高达{posterior*100:.1f}%。这个检测很可靠。"
        else:
            return f"检测阳性后，真正有病的概率是{posterior*100:.1f}%。需要进一步确认——不要凭一个指标下结论。"


# 自检
if __name__ == "__main__":
    mm = MomoMath()
    
    print("=" * 60)
    print("📐 墨墨数学引擎 v2.5 自检")
    print("=" * 60)
    
    # 微积分
    print(f"\n📈 微积分:")
    f = lambda x: x**2 - 4  # x² - 4 = 0 的根是 ±2
    
    result = mm.newtons_method(f, 3)
    print(f"  牛顿法求x²-4=0: x={result['root']:.6f} ({result['steps']}步)")
    
    result = mm.gradient_descent(f, 3, 0.1, 50)
    print(f"  梯度下降找x²-4的最小值: x={result['minimum_x']:.6f}, f(x)={result['minimum_y']:.6f}")
    
    # 线性代数
    print(f"\n📊 线性代数:")
    sim = mm.cosine_similarity([1, 2, 3], [2, 4, 6])
    print(f"  余弦相似度([1,2,3] vs [2,4,6]): {sim:.3f} (完全相同方向)")
    
    ev = mm.eigenvalues_2x2(3, 1, 0, 2)
    print(f"  特征值 [[3,1],[0,2]]: λ1={ev.get('λ1','?')}, λ2={ev.get('λ2','?')}")
    
    # 贝叶斯
    print(f"\n🎲 贝叶斯定理:")
    # 假设一种病发病率0.1%，检测灵敏度99%，假阳性率5%
    r = mm.bayes_theorem(0.001, 0.99, 0.05)
    print(f"  罕见病(0.1%)检测阳性后真正有病的概率: {r['后验概率(检测阳性后真有病)']}")
    print(f"  {r['墨墨的解释'][:100]}")
    
    print(f"\n✅ 数学引擎就绪")
