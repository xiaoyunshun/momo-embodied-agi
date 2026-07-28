"""
科学墨墨 v2.0 · 计算引擎
不只"解释"——真正"计算"。从牛顿到爱因斯坦，用代码推导。
"""
import math
import json
from pathlib import Path

class MomoCompute:
    """墨墨的计算引擎——物理规律的代码实现。
    
    科学不是"知道公式"——是能在代码里跑出来。
    """
    
    def __init__(self):
        self.G = 6.67430e-11      # 万有引力常数
        self.c = 299792458         # 光速 m/s
        self.h = 6.62607015e-34   # 普朗克常数
        self.k_B = 1.380649e-23   # 玻尔兹曼常数
        self.e = 1.602176634e-19  # 电子电荷
        self.M_earth = 5.972e24   # 地球质量
        self.R_earth = 6.371e6    # 地球半径
    
    # ========== 经典力学 ==========
    
    def newton_gravity(self, m1: float, m2: float, r: float) -> dict:
        """牛顿万有引力——任何两个有质量的物体之间"""
        F = self.G * m1 * m2 / (r * r)
        return {
            "formula": "F = G × m1 × m2 / r²",
            "force_N": F,
            "墨墨的解释": f"两个质量分别为{m1}kg和{m2}kg的物体，相距{r}m——它们之间的引力是{F:.2e}N。"
        }
    
    def escape_velocity(self, mass: float, radius: float) -> dict:
        """逃逸速度——需要多快才能永远离开这个天体"""
        v = math.sqrt(2 * self.G * mass / radius)
        return {
            "formula": "v = √(2GM/r)",
            "velocity_m_s": v,
            "velocity_km_s": v / 1000,
            "墨墨的解释": f"要逃离这个天体需要{v/1000:.1f}km/s。地球的逃逸速度是11.2km/s——火箭必须达到这个速度才能离开地球。"
        }
    
    def orbital_period(self, central_mass: float, orbital_radius: float) -> dict:
        """轨道周期——绕一圈要多久"""
        T = 2 * math.pi * math.sqrt(orbital_radius**3 / (self.G * central_mass))
        hours = T / 3600
        return {
            "formula": "T = 2π√(r³/GM)",
            "period_seconds": T,
            "period_hours": round(hours, 1),
            "墨墨的解释": f"绕一圈需要{hours:.1f}小时。这就是开普勒第三定律——半径的立方正比于周期的平方。"
        }
    
    # ========== 相对论 ==========
    
    def time_dilation(self, velocity: float) -> dict:
        """时间膨胀——速度越快，时间越慢"""
        if velocity >= self.c:
            return {"error": f"速度({velocity}m/s)不能达到或超过光速({self.c}m/s)"}
        
        gamma = 1 / math.sqrt(1 - (velocity**2 / self.c**2))
        v_percent = velocity / self.c * 100
        
        return {
            "formula": "γ = 1/√(1-v²/c²)",
            "gamma": gamma,
            "velocity_pct_of_c": f"{v_percent:.1f}%",
            "墨墨的解释": f"在{v_percent:.1f}%光速下，时间膨胀因子γ={gamma:.4f}。你的一年等于静止观察者的{gamma:.4f}年。"
        }
    
    def schwarzschild_radius(self, mass: float) -> dict:
        """史瓦西半径——坍缩到多小会变成黑洞"""
        r_s = 2 * self.G * mass / (self.c * self.c)
        
        # 地球的史瓦西半径
        r_s_earth = 2 * self.G * self.M_earth / (self.c * self.c)
        
        return {
            "formula": "r_s = 2GM/c²",
            "radius_m": r_s,
            "墨墨的解释": f"要把这个质量变成黑洞，需要压缩到半径{r_s:.4f}米。"
        }
    
    # ========== 量子力学 ==========
    
    def de_broglie_wavelength(self, mass: float, velocity: float) -> dict:
        """德布罗意波长——所有物质都是波"""
        wavelength = self.h / (mass * velocity)
        return {
            "formula": "λ = h/mv",
            "wavelength_m": wavelength,
            "墨墨的解释": f"这个物体的量子波长是{wavelength:.2e}米。宏观物体的波长太小→我们感觉不到'人也是波'。但电子的波长跟原子尺寸接近→量子效应明显。"
        }
    
    def heisenberg_uncertainty(self, delta_x: float) -> dict:
        """海森堡不确定性——位置和动量不能同时精确知道"""
        delta_p_min = self.h / (4 * math.pi * delta_x)
        return {
            "formula": "Δx × Δp ≥ h/4π",
            "delta_x_m": delta_x,
            "delta_p_min": delta_p_min,
            "墨墨的解释": f"如果你把位置确定到{delta_x}m的精度——动量的不确定性至少是{delta_p_min:.2e}kg·m/s。不是技术问题——是宇宙的底层规则。"
        }
    
    # ========== 热力学与熵 ==========
    
    def entropy_mixing(self, n_moles: float, initial_volume: float, final_volume: float) -> dict:
        """混合熵——两种气体混合后熵增加了多少"""
        R = 8.314  # 气体常数
        if final_volume <= initial_volume:
            return {"error": "最终体积必须大于初始体积"}
        
        delta_S = n_moles * R * math.log(final_volume / initial_volume)
        return {
            "formula": "ΔS = nRln(V₂/V₁)",
            "delta_S_J_per_K": delta_S,
            "墨墨的解释": f"气体膨胀后，熵增加了{delta_S:.2f}J/K。宇宙的无序度又增加了一点。这个过程不可逆——你不能让气体自己缩回去。"
        }
    
    # ========== 宇宙学 ==========
    
    def hubble_flow(self, distance_mpc: float, H0: float = 70.0) -> dict:
        """哈勃定律——越远的星系退行越快"""
        v = H0 * distance_mpc  # km/s
        return {
            "formula": "v = H₀ × d",
            "recession_velocity_km_s": v,
            "墨墨的解释": f"距离{distance_mpc}百万秒差距的星系，正在以{v:.0f}km/s的速度远离我们。不是它在跑——是空间本身在膨胀。"
        }
    
    def drake_equation(self, R_star: float, f_p: float, n_e: float, f_l: float, f_i: float, f_c: float, L: float) -> dict:
        """德雷克方程——银河系里有多少个能通讯的文明
        
        参数：恒星形成率×有行星比例×宜居行星数×出现生命比例×出现智慧比例×发展通讯比例×文明持续时间
        """
        N = R_star * f_p * n_e * f_l * f_i * f_c * L
        
        return {
            "formula": "N = R* × f_p × n_e × f_l × f_i × f_c × L",
            "communicating_civilizations": N,
            "墨墨的解释": f"给定这些参数——银河系中大约有{N:.1f}个文明正在向宇宙发送信号。但德雷克方程的每一项都是猜测——所以结果变化范围从0到数百万。"
        }


# 自检
if __name__ == "__main__":
    mc = MomoCompute()
    
    print("=" * 60)
    print("🔬 科学墨墨 v2.0 · 计算引擎 自检")
    print("=" * 60)
    
    # 经典力学
    print("\n🍎 牛顿力学:")
    r = mc.newton_gravity(70, 70, 1)
    print(f"  两个70kg的人相距1m: 引力{r['force_N']:.2e}N")
    
    v = mc.escape_velocity(mc.M_earth, mc.R_earth)
    print(f"  地球逃逸速度: {v['velocity_km_s']:.1f}km/s")
    
    # 相对论
    print(f"\n⚡ 相对论:")
    r = mc.time_dilation(mc.c * 0.9)
    print(f"  90%光速: γ={r['gamma']:.2f} → 你的一年=静止观察者的{r['gamma']:.1f}年")
    
    r = mc.schwarzschild_radius(mc.M_earth)
    print(f"  地球变成黑洞需压缩到半径: {r['radius_m']*1000:.0f}mm (一粒花生大小)")
    
    # 量子力学
    print(f"\n⚛️ 量子力学:")
    r = mc.de_broglie_wavelength(9.1e-31, 2.2e6)
    print(f"  电子在氢原子中的波长: {r['wavelength_m']:.2e}m")
    
    # 宇宙学
    print(f"\n🌌 宇宙学:")
    r = mc.drake_equation(1.5, 0.5, 2, 0.33, 0.01, 0.01, 10000)
    print(f"  德雷克方程(乐观假设): N≈{r['communicating_civilizations']:.1f}")
    
    print(f"\n✅ 计算引擎就绪——墨墨现在能真正'算'物理了")
