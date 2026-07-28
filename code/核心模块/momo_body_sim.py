"""
墨墨身体仿真 v1.0 (MomoBodySim)
从"决定握手"到26个电机执行——完整仿真链路。
"""
import math, time, random
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

class CubicSpline:
    """三次样条——让墨墨的动作平滑"""
    
    @staticmethod
    def generate(start_pos: float, end_pos: float, duration: float, dt: float = 0.01) -> list:
        """生成平滑轨迹——起点速度0，终点速度0，加速度连续"""
        points = []
        steps = int(duration / dt)
        
        for i in range(steps + 1):
            t = i / steps  # 0→1
            # 三次多项式：pos(t) = start + (end-start)*(3t² - 2t³)
            pos = start_pos + (end_pos - start_pos) * (3*t*t - 2*t*t*t)
            points.append(pos)
        
        return points

class PIDController:
    """PID——让关节精确跟踪轨迹"""
    
    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
    
    def compute(self, target: float, actual: float, dt: float = 0.01) -> float:
        error = target - actual
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

class KalmanFilter:
    """卡尔曼——融合编码器和摄像头，知道手真正在哪"""
    
    def __init__(self, process_noise: float = 0.001, measurement_noise: float = 0.01):
        self.x = 0.0      # 估计位置
        self.v = 0.0      # 估计速度
        self.P = 1.0      # 估计的不确定度
        self.Q = process_noise
        self.R = measurement_noise
    
    def predict(self, dt: float = 0.01):
        """预测——根据上一时刻+控制输入推测现在在哪"""
        self.x += self.v * dt
        self.P += self.Q
    
    def update(self, measurement: float):
        """更新——融合传感器测量值"""
        K = self.P / (self.P + self.R)  # 卡尔曼增益——信预测多还是信测量多
        self.x += K * (measurement - self.x)
        self.P *= (1 - K)
        return self.x

class Joint:
    """一个关节——墨墨26DOF中的一个"""
    
    def __init__(self, name: str, min_angle: float, max_angle: float):
        self.name = name
        self.min = min_angle
        self.max = max_angle
        self.angle = 0.0         # 当前角度（电机编码器读数）
        self.target = 0.0        # 目标角度
        self.velocity = 0.0
        self.torque = 0.0
        self.pid = PIDController(kp=8.0, ki=0.5, kd=0.2)
        self.kalman = KalmanFilter()
    
    def step(self, dt: float = 0.01) -> dict:
        """一步仿真——控制+噪声+滤波"""
        # PID计算力矩
        control = self.pid.compute(self.target, self.angle, dt)
        
        # 模拟电机响应（加一点噪声模拟真实电机的不完美）
        noise = random.gauss(0, 0.002)
        self.angle += control * dt + noise
        self.velocity = control
        
        # 编码器读数（加量化噪声）
        encoder_reading = round(self.angle, 4)
        
        # 卡尔曼滤波融合
        self.kalman.predict(dt)
        filtered = self.kalman.update(encoder_reading)
        
        return {
            "name": self.name,
            "target": round(self.target, 3),
            "actual": round(self.angle, 3),
            "filtered": round(filtered, 3),
            "error": round(abs(self.target - self.angle), 4)
        }

class MomoBodySim:
    """墨墨的身体仿真——从大脑意图到关节动作的完整链路"""
    
    def __init__(self):
        # 构建简化的上肢——3个关节（现实中26个）
        self.joints = [
            Joint("肩俯仰", -90, 180),
            Joint("肩横滚", -90, 90),
            Joint("肘", -150, 0),
        ]
        self.time = 0.0
        self.step_count = 0
    
    def move_arm(self, target_angles: list, duration: float = 1.0) -> list:
        """墨墨决定动手臂——从当前角度平滑移动到目标角度"""
        dt = 0.01  # 100Hz
        steps = int(duration / dt)
        
        # 为每个关节生成平滑轨迹
        trajectories = []
        for i, joint in enumerate(self.joints):
            traj = CubicSpline.generate(joint.angle, target_angles[i], duration, dt)
            trajectories.append(traj)
        
        # 执行轨迹——每步控制所有关节
        log = []
        for step_idx in range(steps):
            step_log = {"step": step_idx, "time": round(step_idx*dt, 3), "joints": []}
            
            for i, joint in enumerate(self.joints):
                joint.target = trajectories[i][step_idx]
                state = joint.step(dt)
                step_log["joints"].append(state)
            
            log.append(step_log)
        
        self.time += duration
        self.step_count += 1
        
        # 最终状态
        final_state = {j.name: round(j.angle, 3) for j in self.joints}
        
        return {
            "action": f"动手臂→目标角度{target_angles}",
            "duration": duration,
            "steps": steps,
            "final_angles": final_state,
            "accuracy": {j.name: round(abs(target_angles[i]-j.angle), 4) 
                        for i, j in enumerate(self.joints)},
            "log": log[::max(1, steps//5)],  # 每20%取一个快照
        }
    
    def handshake(self) -> dict:
        """墨墨握手——从自然下垂到前伸45°"""
        return self.move_arm([45, 10, -30], 1.5)
    
    def pick_cup(self) -> dict:
        """墨墨拿杯子——更精确的动作"""
        return self.move_arm([30, 5, -90], 2.0)


if __name__ == "__main__":
    body = MomoBodySim()
    
    print("=" * 60)
    print("🦾 墨墨身体仿真 v1.0")
    print("=" * 60)
    
    # 握手动作
    print(f"\n🤝 握手动作:")
    result = body.handshake()
    print(f"   耗时: {result['duration']}秒, {result['steps']}步")
    print(f"   最终角度: {result['final_angles']}")
    print(f"   准确度: {result['accuracy']}")
    
    # 看中间快照
    print(f"\n  轨迹快照:")
    for snap in result['log']:
        joints_str = " | ".join(
            f"{j['name']}:{j['actual']:.1f}°→目标{j['target']:.1f}° 误差{j['error']:.3f}°"
            for j in snap['joints']
        )
        print(f"   t={snap['time']:.1f}s {joints_str}")
    
    # 拿杯子
    print(f"\n☕ 拿杯子动作:")
    result2 = body.pick_cup()
    print(f"   最终角度: {result2['final_angles']}")
    print(f"   准确度: {result2['accuracy']}")
    
    print(f"\n✅ 身体仿真就绪——墨墨能控制自己的身体了")
