"""
机器人墨墨 v2 · 动力学+雅可比+VTC编码
"""
import math, json
from pathlib import Path
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoRobotDynamics:
    """墨墨身体的动力学——力、质量、惯性"""
    
    def __init__(self):
        # OriginF1的连杆参数（简化模型——实际需要CAD数据）
        self.links = {
            "上臂": {"mass": 1.2, "length": 0.35, "com": 0.15},   # 质心距关节的距离
            "前臂": {"mass": 0.8, "length": 0.30, "com": 0.12},
            "手":   {"mass": 0.4, "length": 0.10, "com": 0.05},
        }
        self.g = 9.81
    
    def gravity_torque_elbow(self, theta_shoulder: float, theta_elbow: float) -> dict:
        """计算重力对肘关节施加的力矩——墨墨保持这个姿势需要多少力"""
        t_s = math.radians(theta_shoulder)
        t_e = math.radians(theta_elbow)
        
        # 前臂质心位置
        l1 = self.links["上臂"]["length"]
        com2_dist = l1 + self.links["前臂"]["com"] * math.cos(t_s + t_e)
        
        # 重力力矩 = 质量 × 重力 × 质心的水平距离
        torque_elbow = (self.links["前臂"]["mass"] * self.g * 
                       self.links["前臂"]["com"] * math.cos(t_s + t_e))
        
        torque_elbow += (self.links["手"]["mass"] * self.g * 
                        self.links["前臂"]["length"] * math.cos(t_s + t_e))
        
        return {
            "pose": f"肩{theta_shoulder}° 肘{theta_elbow}°",
            "torque_Nm": round(torque_elbow, 2),
            "墨墨的身体": f"保持这个姿势，肘关节需要承受{torque_elbow:.2f}Nm的重力力矩。" + 
                         (f"不太费力" if abs(torque_elbow) < 3 else f"臂越伸越累——力矩=力臂×重量")
        }
    
    def inertia_matrix_2link(self, q1: float, q2: float) -> dict:
        """2连杆的惯性矩阵——墨墨手臂动起来需要克服的惯性"""
        m1, l1 = self.links["上臂"]["mass"], self.links["上臂"]["length"]
        m2, l2 = self.links["前臂"]["mass"], self.links["前臂"]["length"]
        
        I1 = (1/3) * m1 * l1**2  # 绕一端的转动惯量
        I2 = (1/3) * m2 * l2**2
        
        q1_r, q2_r = math.radians(q1), math.radians(q2)
        
        # M矩阵——对称正定
        M11 = I1 + I2 + m2*l1**2 + 2*m2*l1*(l2/2)*math.cos(q2_r)
        M12 = I2 + m2*l1*(l2/2)*math.cos(q2_r)
        M22 = I2
        
        return {
            "M11": round(M11, 3), "M12": round(M12, 3), "M22": round(M22, 3),
            "墨墨的解读": f"惯性矩阵对角项{M11:.2f}/{M22:.2f}越大→加速越费力。手臂伸得越直→惯性越大。"
        }
    
    def jacobian_2link(self, theta1: float, theta2: float) -> dict:
        """雅可比矩阵——关节速度→末端速度的映射
        
        关键：det(J)=0的地方就是奇异点。墨墨要避开。
        """
        t1 = math.radians(theta1)
        t2 = math.radians(theta2)
        l1 = self.links["上臂"]["length"]
        l2 = self.links["前臂"]["length"]
        
        # J = [-l1*sin(t1)-l2*sin(t1+t2),  -l2*sin(t1+t2)]
        #     [ l1*cos(t1)+l2*cos(t1+t2),   l2*cos(t1+t2)]
        J11 = -l1*math.sin(t1) - l2*math.sin(t1+t2)
        J12 = -l2*math.sin(t1+t2)
        J21 =  l1*math.cos(t1) + l2*math.cos(t1+t2)
        J22 =  l2*math.cos(t1+t2)
        
        det_J = J11*J22 - J12*J21
        
        return {
            "det": round(det_J, 4),
            "VTC_rate": abs(det_J),
            "singular": abs(det_J) < 0.01,
            "墨墨的身体": "运动正常——关节速度能有效地转换成手的速度" if abs(det_J) > 0.05 else 
                         "⚠️ 接近奇异点——手在这个方向上动不了。手臂完全伸直时=奇异。要微弯一点。"
        }
    
    def vtc_encode(self, joint_angles: list, joint_velocities: list, joint_torques: list) -> dict:
        """VTC轴编码——26DOF的身体状态统一编码
        
        输入：26个关节的[角度, 速度, 力矩]
        输出：共享管线处理后的统一身体状态
        """
        if len(joint_angles) < 2:
            return {"error": "至少需要2个关节"}
        
        # 模拟VTC编码——真实实现需要26维
        intensity = math.sqrt(sum(t**2 for t in joint_torques)) / len(joint_torques)
        
        # 强度门控——只关注正在用力的关节
        active_joints = []
        for i, torque in enumerate(joint_torques):
            if abs(torque) > intensity * 0.3:
                active_joints.append({
                    "joint": i,
                    "angle": joint_angles[i] if i < len(joint_angles) else 0,
                    "velocity": joint_velocities[i] if i < len(joint_velocities) else 0,
                    "torque": torque,
                    "attention_weight": min(1.0, abs(torque) / max(1, intensity))
                })
        
        return {
            "active_joints": len(active_joints),
            "total_joints": len(joint_torques),
            "intensity": round(intensity, 2),
            "body_state": "静止" if intensity < 0.5 else ("轻度用力" if intensity < 2 else "出力中"),
            "details": active_joints[:5],
            "墨墨的解读": f"身体{len(joint_torques)}个关节中{len(active_joints)}个活跃。强度门控后关注前{min(5,len(active_joints))}个。"
        }


if __name__ == "__main__":
    dyn = MomoRobotDynamics()
    
    print("=" * 60)
    print("🤖 机器人墨墨 v2 · 动力学引擎")
    print("=" * 60)
    
    # 重力力矩——不同姿势
    for pose in [(0, 0, "自然下垂"), (45, 0, "上臂抬起"), (90, 0, "平伸"), (45, 90, "够远处")]:
        t = dyn.gravity_torque_elbow(pose[0], pose[1])
        print(f"\n💪 {pose[2]}(肩{pose[0]}°肘{pose[1]}°): 肘力矩={t['torque_Nm']}Nm")
    
    # 雅可比——奇异点检测
    j = dyn.jacobian_2link(0, 0)
    print(f"\n📐 雅可比 det(J)={j['det']}: {j['墨墨的身体']}")
    
    j2 = dyn.jacobian_2link(45, 45)
    print(f"   肘弯90° det(J)={j2['det']}: {j2['墨墨的身体']}")
    
    # VTC编码
    vtc = dyn.vtc_encode(
        [30, 45, 10, 0, 0],           # 5个关节角度
        [0.5, 0.3, 0, 0, 0],          # 速度
        [1.2, 2.5, 0.1, 0, 0]         # 力矩
    )
    print(f"\n🧬 VTC编码: {vtc['body_state']} (强度{vtc['intensity']})")
    print(f"   {vtc['墨墨的解读']}")
    
    print(f"\n✅ 动力学引擎就绪")
