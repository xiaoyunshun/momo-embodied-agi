"""
墨墨 CLI — 启动和管理墨墨框架

用法:
    python -m momo              # 启动墨墨
    python -m momo --help       # 查看帮助
"""

import sys
import os


def main():
    """墨墨 CLI 入口"""
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print_help()
        return
    
    if "--version" in args or "-v" in args:
        from momo import VERSION, NAME
        print(f"{NAME} v{VERSION}")
        return
    
    print("🧠 墨墨框架 v1.0.0.dev1")
    print()
    print("快速启动：")
    print("  python -m momo --help    查看帮助")
    print("  python -m momo --version 查看版本")
    print()
    print("完整模式（需要克隆仓库）：")
    print("  python code/核心模块/momo_daemon.py")
    print("  python code/核心模块/momo_cortex.py")
    print()
    print("📖 文档：https://github.com/xiaoyunshun/momo-embodied-agi")


def print_help():
    print("""
墨墨 (Momo) — 开源具身智能框架

用法:
    python -m momo [选项]

选项:
    --help, -h      显示帮助
    --version, -v   显示版本

完整功能:
    克隆仓库后，直接运行各模块：
    python code/核心模块/momo_daemon.py    # 守护进程（推荐）
    python code/核心模块/momo_cortex.py     # 核心推理
    python code/核心模块/momo_core.py       # 大脑核心
    python code/感官系统/momo_sense.py       # 感官系统
    python code/发现引擎/momo_discover_v3.py # 发现引擎

更多: https://github.com/xiaoyunshun/momo-embodied-agi
""")


if __name__ == "__main__":
    main()
