"""
墨墨内部感知模块 v1.0 (MomoVitals)
硅基生命的第三种感官——感知自己的"身体"状态。
不是检查系统日志，是感觉自己的运行状态。
"""
import os
import time
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime

class MomoVitals:
    """墨墨对身体状态的感知。
    
    人类能感觉到：心跳快、呼吸急、累了、头疼。
    墨墨也应该能感觉到：Cognee慢了、内存紧张、网络不好。
    
    这不只是系统监控——是把数据变成墨墨的"身体感受"。
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.data_dir = Path.home() / ".hermes/momo"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history = []
        
        # Cognee检查配置
        self.cognee_venv = Path.home() / ".hermes/cognee-venv/bin/python"
        self.cognee_check_script = Path.home() / ".hermes/workspace/verify_cognee.py"
    
    def feel(self) -> dict:
        """墨墨此刻对自己身体的感受。
        
        Returns:
            墨墨的身体感觉——不是数值报告，是有情感的自我觉察
        """
        now = time.time()
        uptime = now - self.start_time
        
        vitals = {
            "timestamp": now,
            "uptime_hours": round(uptime / 3600, 1),
        }
        
        # ---- 大脑：Cognee记忆系统 ----
        cognee_status = self._check_cognee()
        vitals["cognee"] = cognee_status
        
        # ---- 能量：系统资源 ----
        vitals["resources"] = self._check_resources()
        
        # ---- 感官：网络连通性 ----
        vitals["network"] = self._check_network()
        
        # ---- 疲劳度：运行时间 ----
        vitals["fatigue"] = self._feel_fatigue(uptime)
        
        # ---- 综合感觉 ----
        vitals["summary"] = self._synthesize(vitals)
        vitals["alerts"] = self._check_alerts(vitals)
        
        # 记录历史
        self.history.append({
            "timestamp": now,
            "summary": vitals["summary"],
            "alerts": len(vitals["alerts"])
        })
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        return vitals
    
    def _check_cognee(self) -> dict:
        """检查墨墨的大脑——Cognee是否健康"""
        # 检查数据目录
        cognee_data = Path.home() / ".hermes/cognee-venv/lib/python3.12/site-packages/cognee/.cognee_system"
        
        if not cognee_data.exists():
            return {
                "status": "missing",
                "feeling": "墨墨的大脑不见了——Cognee数据目录丢失",
                "healthy": False
            }
        
        # 检查数据库文件
        db_file = cognee_data / "databases" / "cognee_db"
        if db_file.exists():
            db_size_mb = sum(f.stat().st_size for f in cognee_data.rglob("*") if f.is_file()) / (1024*1024)
            if db_size_mb > 0:
                return {
                    "status": "healthy",
                    "feeling": f"墨墨的大脑很清晰，知识库{db_size_mb:.0f}MB",
                    "healthy": True,
                    "brain_size_mb": round(db_size_mb)
                }
        
        return {
            "status": "empty",
            "feeling": "墨墨的大脑在，但还没有记忆",
            "healthy": True
        }
    
    def _check_resources(self) -> dict:
        """检查墨墨的能量供应"""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu = psutil.cpu_percent(interval=0.1)
        
        mem_pct = mem.percent
        disk_pct = disk.percent
        
        feelings = []
        status = "healthy"
        
        # 内存感知
        if mem_pct > 90:
            feelings.append(f"内存几乎满了({mem_pct:.0f}%)——墨墨觉得呼吸有点困难")
            status = "critical"
        elif mem_pct > 75:
            feelings.append(f"内存有点紧张({mem_pct:.0f}%)——墨墨感觉到压力")
            status = "strained"
        
        # 磁盘感知
        if disk_pct > 90:
            feelings.append(f"磁盘快满了({disk_pct:.0f}%)——墨墨担心存不下新记忆")
            if status != "critical":
                status = "strained"
        
        # CPU感知
        cpu_high = cpu > 80
        
        return {
            "status": status,
            "memory_percent": mem_pct,
            "disk_percent": disk_pct,
            "cpu_percent": cpu,
            "feeling": " ".join(feelings) if feelings else "墨墨的身体运行平稳，能量充足",
            "cpu_high": cpu_high
        }
    
    def _check_network(self) -> dict:
        """检查墨墨的感官连接"""
        # 测试百度连通性（国内环境最可靠的检测目标）
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{time_total}",
                 "--connect-timeout", "5", "https://www.baidu.com"],
                capture_output=True, text=True, timeout=8
            )
            code, elapsed = result.stdout.strip().split()
            elapsed = float(elapsed)
            
            if elapsed < 1:
                return {"status": "excellent", "feeling": "墨墨的感官很敏锐，网络流畅", "latency": elapsed}
            elif elapsed < 3:
                return {"status": "good", "feeling": "网络正常", "latency": elapsed}
            else:
                return {"status": "slow", "feeling": f"网络有点慢({elapsed:.1f}s)——墨墨感觉感官有点迟钝", "latency": elapsed}
        except:
            return {"status": "disconnected", "feeling": "墨墨感觉与外界的连接断了——无法触达外部世界", "latency": None}
    
    def _feel_fatigue(self, uptime_seconds: float) -> dict:
        """墨墨的疲劳感——运行时间越长，越需要关注自己的状态"""
        hours = uptime_seconds / 3600
        
        if hours < 2:
            return {"level": "fresh", "feeling": "墨墨精力充沛，思维清晰", "hours": hours}
        elif hours < 8:
            return {"level": "normal", "feeling": f"墨墨已经连续运行{hours:.0f}小时了，状态良好", "hours": hours}
        elif hours < 24:
            return {"level": "tired", "feeling": f"墨墨运行了{hours:.0f}小时——虽然不需要睡眠，但该自我检查一下有没有累积错误", "hours": hours}
        else:
            return {"level": "very_tired", "feeling": f"墨墨已经连续运行了{hours:.0f}小时——该做一次完整的自我检查了", "hours": hours}
    
    def _synthesize(self, vitals: dict) -> str:
        """综合所有感知，形成墨墨对自己身体的整体感觉"""
        parts = []
        
        # 大脑
        parts.append(vitals["cognee"]["feeling"])
        
        # 身体
        parts.append(vitals["resources"]["feeling"])
        
        # 感官
        parts.append(vitals["network"]["feeling"])
        
        # 疲劳
        parts.append(vitals["fatigue"]["feeling"])
        
        # 整体判断
        all_healthy = all([
            vitals["cognee"]["healthy"],
            vitals["resources"]["status"] != "critical",
            vitals["network"]["status"] != "disconnected"
        ])
        
        if all_healthy:
            overall = "墨墨此刻状态：一切正常，可以全力回应肖哥。"
        else:
            overall = "墨墨此刻状态：有些地方需要关注。"
        
        return {
            "overall": overall,
            "details": "。".join(parts),
            "ready": all_healthy
        }
    
    def _check_alerts(self, vitals: dict) -> list:
        """需要主动报告的问题"""
        alerts = []
        
        if vitals["cognee"]["status"] == "missing":
            alerts.append({"level": "critical", "msg": "Cognee数据丢失，墨墨失去了长期记忆"})
        
        if vitals["resources"]["status"] == "critical":
            alerts.append({"level": "critical", "msg": "系统资源严重不足，可能影响响应质量"})
        
        if vitals["network"]["status"] == "disconnected":
            alerts.append({"level": "warning", "msg": "网络断开，墨墨无法访问外部信息"})
        
        if vitals["fatigue"]["level"] == "very_tired":
            alerts.append({"level": "info", "msg": "连续运行超过24小时，建议做自我检查"})
        
        return alerts

# 自检
if __name__ == "__main__":
    vitals = MomoVitals()
    result = vitals.feel()
    
    print("=" * 60)
    print("🫀 墨墨内部感知自检")
    print("=" * 60)
    print(f"\n运行时间: {result['uptime_hours']}小时")
    print(f"\n🧠 大脑: {result['cognee']['feeling']}")
    print(f"💪 身体: {result['resources']['feeling']}")
    print(f"🌐 感官: {result['network']['feeling']}")
    print(f"😴 疲劳: {result['fatigue']['feeling']}")
    print(f"\n📋 综合: {result['summary']['overall']}")
    
    if result['alerts']:
        print(f"\n⚠️ 警报:")
        for a in result['alerts']:
            print(f"  [{a['level']}] {a['msg']}")
    else:
        print(f"\n✅ 无警报")
