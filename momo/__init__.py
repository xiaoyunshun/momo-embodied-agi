"""
墨墨 (Momo) — 开源具身智能框架

五层大脑 + 七感官 + 八分身 + 机器人身体方案 + 发现引擎

使用方式：
    pip install git+https://github.com/xiaoyunshun/momo-embodied-agi.git
    python -m momo

或直接 clone 仓库运行：
    python code/核心模块/momo_daemon.py
"""

__version__ = "1.0.0.dev1"
__author__ = "肖云顺"
__license__ = "Apache 2.0"

# 核心能力快速导入
from . import cli
from .runner import MomoRunner

# 版本信息
VERSION = __version__
NAME = "墨墨 (Momo)"
