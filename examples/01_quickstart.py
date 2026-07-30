"""
示例 1：一分钟上手墨墨

最简单的用法——pip 安装后直接运行。
"""
import sys
from pathlib import Path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# 方式 A：用 Python 包
from momo.runner import MomoRunner

runner = MomoRunner(xiaoge_name="开发者")
result = runner.start()
print(result["message"])

# 交互一次
resp = runner.interact("你好，墨墨！")
print(f"墨墨说: {resp['response']}")
print(f"耗时: {resp['elapsed_seconds']}秒")

# 查看状态
import json
print(json.dumps(runner.status(), ensure_ascii=False, indent=2))

runner.stop()
print("✅ 示例 1 完成")
