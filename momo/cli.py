"""
墨墨 CLI — 启动和管理墨墨框架

用法:
    python -m momo              查看帮助
    python -m momo --version    版本信息
    python -m momo run          启动运行器（带心跳守护进程）
    python -m momo run -i       交互式模式
    python -m momo run --name 肖哥  指定用户名称
"""

import sys
import os


def main():
    """墨墨 CLI 入口"""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args or len(args) == 0:
        print_help()
        return

    if "--version" in args or "-v" in args:
        from momo import VERSION, NAME
        print(f"{NAME} v{VERSION}")
        return

    if args[0] == "run":
        return _run(args[1:])

    print(f"未知命令: {args[0]}\n")
    print_help()


def _run(args: list):
    """启动运行器"""
    import argparse

    parser = argparse.ArgumentParser(description="启动墨墨运行器")
    parser.add_argument("--name", "-n", default="用户", help="用户名称")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="交互式模式"
    )
    parsed, unknown = parser.parse_known_args(args)

    from momo.runner import MomoRunner

    runner = MomoRunner(xiaoge_name=parsed.name)
    result = runner.start()
    print(f"🧠 {result['message']}")

    if parsed.interactive:
        print("\n输入 'exit' 退出，输入 'status' 查看状态\n")
        try:
            while True:
                text = input(">>> ")
                if text.lower() in ("exit", "quit", "q"):
                    break
                if text.lower() == "status":
                    import json
                    print(json.dumps(runner.status(), ensure_ascii=False, indent=2))
                    continue
                resp = runner.interact(text)
                print(f"墨墨: {resp['response']}")
        except (KeyboardInterrupt, EOFError):
            pass

    runner.stop()
    print("🛑 墨墨已停止")


def print_help():
    print("""
墨墨 (Momo) — 开源具身智能框架

用法:
    python -m momo [命令] [选项]

命令:
    run                 启动运行器（后台心跳 + 分身系统）
    run --interactive   交互式模式
    run --name <名字>   指定用户名称
    --version, -v       显示版本

示例:
    python -m momo run
    python -m momo run -i
    python -m momo run --name 肖哥 -i

完整功能（需要克隆仓库）:
    python code/核心模块/momo_daemon.py    # 守护进程（推荐）
    python code/核心模块/momo_cortex.py     # 核心推理

pip 安装:
    pip install git+https://github.com/xiaoyunshun/momo-embodied-agi.git
    python -m momo run -i

更多: https://github.com/xiaoyunshun/momo-embodied-agi
""")


if __name__ == "__main__":
    main()
