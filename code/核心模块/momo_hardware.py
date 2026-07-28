"""
墨墨硬件抽象层 v1.0 (MomoHardware)
软件感官→物理设备的翻译层。
换什么硬件都不影响墨墨的上层感官。
"""
import json, time, threading, queue
from pathlib import Path
from datetime import datetime, timedelta, timezone
from enum import Enum

BEIJING_TZ = timezone(timedelta(hours=8))

class SensorType(Enum):
    CAMERA = "camera"
    MICROPHONE = "microphone"
    THERMAL = "thermal"
    PRESSURE = "pressure"
    IMU = "imu"  # 惯性测量——知道自己的姿态
    TOUCH = "touch"

class MomoHardware:
    """墨墨的硬件抽象层——所有感官的物理接口。
    
    每个传感器是一个Driver。
    墨墨的上层感官（Vision/Hearing/Sense）不直接跟硬件打交道——
    它们通过这个抽象层获取数据。
    """
    
    def __init__(self):
        self.drivers = {}         # 传感器ID→Driver
        self.streams = {}         # 传感器ID→数据流队列
        self.running = False
        self.hardware_config = self._load_config()
    
    def _load_config(self):
        config_path = Path.home() / ".hermes/momo/hardware_config.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
        return {
            "available": {
                "camera": {"status": "未连接", "resolution": "待配置"},
                "microphone": {"status": "未连接", "sample_rate": "待配置"},
                "thermal": {"status": "未连接"},
                "pressure": {"status": "未连接", "locations": []},
                "imu": {"status": "未连接"},
                "touch": {"status": "未连接"},
            },
            "body_type": "未选定",  # OriginF1 / U1Pro / 定制
            "face_display": "未连接",  # 表情屏
            "speaker": "未连接",
        }
    
    def register_driver(self, sensor_type: SensorType, driver_id: str, driver_config: dict):
        """注册一个传感器驱动"""
        self.drivers[driver_id] = {
            "type": sensor_type.value,
            "config": driver_config,
            "status": "registered",
            "last_data": None,
            "registered_at": datetime.now(BEIJING_TZ).isoformat()
        }
        self.streams[driver_id] = queue.Queue(maxsize=100)
        return {"registered": driver_id, "type": sensor_type.value}
    
    def start_stream(self, driver_id: str, callback=None):
        """启动一个数据流——持续从传感器获取数据"""
        if driver_id not in self.drivers:
            return {"error": f"Driver {driver_id} 未注册"}
        
        def _stream_loop():
            """模拟硬件数据流——有真实硬件后换成真实驱动"""
            driver = self.drivers[driver_id]
            sensor_type = driver["type"]
            
            while self.running:
                try:
                    # 占位——真实硬件会从设备读取
                    data = self._mock_read(sensor_type)
                    self.streams[driver_id].put(data, timeout=1)
                    if callback:
                        callback(driver_id, data)
                except queue.Full:
                    pass  # 队列满了就丢旧数据
                except Exception as e:
                    break
                
                time.sleep(0.1)  # 100ms采样间隔
        
        thread = threading.Thread(target=_stream_loop, daemon=True)
        thread.start()
        
        return {"streaming": driver_id, "rate": "100ms"}
    
    def _mock_read(self, sensor_type: str) -> dict:
        """模拟硬件读取——有真实硬件后换成实际驱动"""
        now = datetime.now(BEIJING_TZ).isoformat()
        
        if sensor_type == "camera":
            return {"type": "frame", "timestamp": now, "data": "待连接摄像头", "resolution": "N/A"}
        elif sensor_type == "microphone":
            return {"type": "audio_chunk", "timestamp": now, "data": "待连接麦克风", "duration_ms": 100}
        elif sensor_type == "thermal":
            return {"type": "temperature", "timestamp": now, "data": "待连接温度传感器", "celsius": None}
        elif sensor_type == "pressure":
            return {"type": "force", "timestamp": now, "data": "待连接压力传感器", "newton": None}
        elif sensor_type == "touch":
            return {"type": "contact", "timestamp": now, "data": "待连接触觉传感器", "location": None}
        elif sensor_type == "imu":
            return {"type": "pose", "timestamp": now, "data": "待连接IMU", "roll_pitch_yaw": None}
        return {"type": "unknown"}
    
    def read_latest(self, driver_id: str) -> dict:
        """获取最新的传感器数据（非阻塞）"""
        if driver_id not in self.streams:
            return {"error": "流未启动"}
        try:
            return self.streams[driver_id].get_nowait()
        except queue.Empty:
            return {"status": "no_new_data"}
    
    # ========== 执行层——墨墨的"动作" ==========
    
    def speak(self, text: str):
        """墨墨说话——通过TTS驱动扬声器"""
        # 当前通过text_to_speech工具——有身体后通过硬件扬声器
        return {"action": "speak", "text": text[:200], "status": "通过TTS输出"}
    
    def express(self, emotion: str):
        """墨墨的表情——如果有面部的显示屏"""
        expressions = {
            "happy": "眼睛弯弯 + 嘴角上扬",
            "concerned": "眉毛微蹙 + 嘴唇微抿",
            "thinking": "稍微歪头 + 眨眼",
            "surprised": "眼睛睁大 + 嘴微张",
            "neutral": "自然 + 偶尔眨眼",
        }
        return {"action": "express", "emotion": emotion, "display": expressions.get(emotion, expressions["neutral"])}
    
    def body_status(self) -> dict:
        return {
            "connected_sensors": len(self.drivers),
            "active_streams": len([d for d in self.drivers if self.drivers[d]["last_data"]]),
            "body_type": self.hardware_config.get("body_type", "未选定"),
            "墨墨的身体状态": "软件就绪——等待硬件接入" if not self.drivers else "部分传感器在线"
        }


if __name__ == "__main__":
    hw = MomoHardware()
    
    print("=" * 60)
    print("🔌 墨墨硬件抽象层 v1.0")
    print("=" * 60)
    
    # 注册一些传感器
    for s in [SensorType.CAMERA, SensorType.MICROPHONE, SensorType.IMU]:
        result = hw.register_driver(s, f"driver_{s.value}", {"location": "头部" if s == SensorType.CAMERA else "身体"})
        print(f"  注册: {result['registered']}")
    
    # 表情测试
    for e in ["happy", "concerned", "thinking"]:
        expr = hw.express(e)
        print(f"  表情[{e}]: {expr['display']}")
    
    print(f"\n{hw.body_status()['墨墨的身体状态']}")
    print(f"\n✅ 硬件抽象层就绪——等待身体")
