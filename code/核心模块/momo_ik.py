"""
墨墨逆运动学引擎 v1.0
从"手到(X,Y,Z)"→"26个关节转多少度"。
"""
import math
from momo_body_sim import MomoBodySim

class MomoInverseKinematics:
    """逆运动学——给定手的位置，算每个关节的角度"""
    
    def __init__(self):
        self.body = MomoBodySim()
        self.L1 = 0.35  # 上臂长度
        self.L2 = 0.30  # 前臂长度
    
    def solve_2link_analytical(self, x: float, y: float) -> dict:
        """解析解——2连杆的逆运动学（余弦定理）
        
        给定：手要在(x, y)
        求：肩角度θ1 和 肘角度θ2
        
        这是26DOF的简化——多出来的自由度产生无数解。
        墨墨会从无数解里选"最自然的"那个。
        """
        r = math.sqrt(x*x + y*y)
        
        # 够不到——太远了
        if r > self.L1 + self.L2:
            return {
                "reachable": False,
                "reason": f"距离{r:.2f}m > 最大{self.L1+self.L2:.2f}m——够不到",
                "墨墨的反应": "墨墨需要靠近一点"
            }
        
        # 太近了——缩不到
        if r < abs(self.L1 - self.L2):
            return {
                "reachable": False,
                "reason": f"距离{r:.2f}m < 最小{abs(self.L1-self.L2):.2f}m——手缩不回来",
                "墨墨的反应": "墨墨需要调整身体位置"
            }
        
        # 余弦定理求肘角
        # c² = a² + b² - 2ab·cos(C)
        # cos(π - θ2) = (L1² + L2² - r²) / (2·L1·L2)
        cos_elbow = (self.L1**2 + self.L2**2 - r**2) / (2 * self.L1 * self.L2)
        theta2 = math.pi - math.acos(max(-1, min(1, cos_elbow)))  # 肘向上（自然姿态）
        
        # 求肩角
        # θ1 = atan2(y, x) - atan2(L2·sin(θ2), L1 + L2·cos(θ2))
        phi = math.atan2(y, x)
        psi = math.atan2(self.L2 * math.sin(theta2), self.L1 + self.L2 * math.cos(theta2))
        theta1 = phi - psi
        
        theta1_deg = math.degrees(theta1)
        theta2_deg = math.degrees(theta2)
        
        # 验证正运动学
        x_check = self.L1*math.cos(theta1) + self.L2*math.cos(theta1+theta2)
        y_check = self.L1*math.sin(theta1) + self.L2*math.sin(theta1+theta2)
        
        return {
            "reachable": True,
            "target": {"x": x, "y": y},
            "solution": {
                "肩角度": round(theta1_deg, 1),
                "肘角度": round(theta2_deg, 1),
            },
            "verification": f"正运动学验证: 手在({x_check:.3f}, {y_check:.3f})——误差{(math.sqrt((x_check-x)**2+(y_check-y)**2)):.4f}m",
            "墨墨的决定": f"肩转{theta1_deg:.0f}° + 肘转{theta2_deg:.0f}° → 手到({x:.2f},{y:.2f})"
        }
    
    def solve_2link_numerical(self, x_target: float, y_target: float, 
                               theta1_init: float = 0, theta2_init: float = 0,
                               max_iter: int = 100) -> dict:
        """数值解——雅可比伪逆迭代法
        
        不需要公式推导。从当前角度出发→算雅可比→算修正量→迭代逼近。
        适用任何DOF——不只是2连杆。
        """
        t1 = math.radians(theta1_init)
        t2 = math.radians(theta2_init)
        alpha = 0.1  # 学习率
        
        history = []
        
        for i in range(max_iter):
            # 正运动学——现在手在哪
            x = self.L1*math.cos(t1) + self.L2*math.cos(t1+t2)
            y = self.L1*math.sin(t1) + self.L2*math.sin(t1+t2)
            
            error_x = x_target - x
            error_y = y_target - y
            error = math.sqrt(error_x**2 + error_y**2)
            
            history.append({"iter": i, "x": round(x,3), "y": round(y,3), "error": round(error,4)})
            
            if error < 0.001:
                return {
                    "method": "数值迭代(雅可比伪逆)",
                    "converged": True,
                    "iterations": i+1,
                    "solution": {"肩角度": round(math.degrees(t1),1), "肘角度": round(math.degrees(t2),1)},
                    "final_error_m": round(error, 4),
                    "history": history[::max(1,i//5)],
                    "墨墨的感觉": f"迭代{i+1}次收敛——手到了目标位置，误差{error*1000:.1f}mm"
                }
            
            # 雅可比矩阵
            J11 = -self.L1*math.sin(t1) - self.L2*math.sin(t1+t2)
            J12 = -self.L2*math.sin(t1+t2)
            J21 =  self.L1*math.cos(t1) + self.L2*math.cos(t1+t2)
            J22 =  self.L2*math.cos(t1+t2)
            
            # 雅可比伪逆——用转置近似（对于方阵就是逆）
            det = J11*J22 - J12*J21
            if abs(det) < 1e-6:
                return {"converged": False, "reason": f"第{i}步遇到奇异点", "history": history}
            
            inv_J11 =  J22 / det
            inv_J12 = -J12 / det
            inv_J21 = -J21 / det
            inv_J22 =  J11 / det
            
            # 关节修正
            dt1 = alpha * (inv_J11*error_x + inv_J12*error_y)
            dt2 = alpha * (inv_J21*error_x + inv_J22*error_y)
            
            t1 += dt1
            t2 += dt2
        
        return {
            "method": "数值迭代",
            "converged": False,
            "iterations": max_iter,
            "final_error_m": round(error, 4),
            "墨墨的感觉": f"迭代{max_iter}次未收敛——可能需要调整初始姿态或学习率"
        }


if __name__ == "__main__":
    ik = MomoInverseKinematics()
    
    print("=" * 60)
    print("📐 墨墨逆运动学引擎 v1.0")
    print("=" * 60)
    
    # 解析解——够杯子
    print(f"\n🧮 解析解——够杯子(0.4, 0.3):")
    result = ik.solve_2link_analytical(0.4, 0.3)
    print(f"   {result['墨墨的决定']}")
    print(f"   {result['verification']}")
    
    # 够不到
    print(f"\n🫸 够不到(1.0, 0.0):")
    result = ik.solve_2link_analytical(1.0, 0.0)
    print(f"   {result.get('reason','')}")
    
    # 数值解——从不同初始姿态出发
    print(f"\n🔢 数值解——从(0°,0°)出发够(0.5, 0.2):")
    result = ik.solve_2link_numerical(0.5, 0.2, 0, 0)
    print(f"   {result['墨墨的感觉']}")
    print(f"   解: 肩{result['solution']['肩角度']}° 肘{result['solution']['肘角度']}°")
    
    print(f"\n✅ 逆运动学引擎就绪")
