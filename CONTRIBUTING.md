# 贡献指南

让墨墨变得更好 — 欢迎你的参与。

---

## 🤔 我能贡献什么？

| 类型 | 适合谁 | 怎么开始 |
|------|--------|---------|
| **🆕 新技能/新分身** | 有特定领域经验的人 | 参考现有分身模块的格式，写一个新的 Python 文件 |
| **🐛 Bug 报告** | 使用中发现问题的人 | 开 Issue，告诉我们你看到了什么 |
| **📖 文档改进** | 想让入门更简单的人 | 提 PR 修改 README 或 docs/ |
| **💡 想法/讨论** | 有场景但不确定怎么落地 | 开一个 GitHub Discussion |
| **🤖 机器人硬件** | 有机械/电子背景的人 | 贡献身体方案或传感器接口 |
| **🌐 翻译** | 想帮助全球用户的人 | 把文档翻译成其他语言 |

---

## 🆕 贡献一个新技能（最快的方式）

分身系统是墨墨最易扩展的部分。写一个新分身 = 一个 Python 文件，注册到系统即可。

### 步骤

```bash
# 1. fork 仓库
# 2. 克隆你的 fork
git clone https://github.com/你的用户名/momo-embodied-agi.git
cd momo-embodied-agi

# 3. 在分身目录下创建你的技能文件
touch code/分身体系/momo_your_skill.py
```

### 模板

```python
"""
你的技能名称
功能描述：一句话说明这个分身做什么
"""

class YourAvatar:
    """你的分身类"""
    
    def __init__(self):
        self.name = "你的分身名称"
        self.version = "1.0.0"
    
    def process(self, input_data):
        """处理输入并返回结果"""
        # 你的逻辑写在这里
        return {"result": "处理完成"}
    
    def help(self):
        """返回这个分身的能力说明"""
        return {
            "name": self.name,
            "description": "我做什么",
            "capabilities": ["能力1", "能力2"]
        }

# 注册到分身系统
if __name__ == "__main__":
    avatar = YourAvatar()
    print(avatar.process("测试输入"))
```

### 质量标准

- ✅ 代码可读，有中文或英文注释
- ✅ 有 `help()` 方法返回能力说明
- ✅ 不依赖墨墨核心以外的大模型 API（除非是你的领域必需）
- ✅ 不包含任何真实 API Key 或凭证

---

## 🐛 报告 Bug

开 Issue 时请包含：

1. **描述** — 发生了什么？预期应该发生什么？
2. **复现步骤** — 怎么重现这个问题
3. **环境** — Python 版本、操作系统、依赖版本
4. **日志/错误信息** — 完整的错误堆栈

---

## 📖 改进文档

文档永远可以更好。如果你发现：

- 某段说明看不懂
- 某个示例跑不通
- 缺少某个功能的说明

直接提 PR 修改 `docs/` 目录或 README.md。

---

## 🏗️ 贡献身体方案

机器人硬件方案在 `docs/方案/` 下。如果你有：

- 新的运动学链配置
- 传感器选型方案
- 安全架构改进
- 生产成本优化

欢迎提交新的技术方案文档。

---

## ⚡ 开发指南

### 环境

```bash
# 推荐 Python 3.10+
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e .
```

### 代码风格

- 文件名：全小写，下划线分隔（momo_skill_name.py）
- 类名：驼峰（MyAvatar）
- 函数名：下划线分隔（process_input）
- 可以写中文注释，和墨墨保持一致

### 提交规范

```
类型(范围): 简短描述

- type: feat / fix / docs / refactor / style / chore
- scope: core / sense / avatar / discovery / docs / robot
- 描述用中文或英文
```

示例：
```
feat(sense): 添加温度感知模块
fix(core): 修复守护进程启动时分身重复注册的问题
docs(readme): 更新快速上手示例
```

---

## 🔄 迭代循环

你的贡献不只是加功能——它是墨墨进化的一部分：

1. 你提交代码 → CI 自动测试
2. 合并后 → 数据（匿名、脱敏）可以贡献回进化引擎
3. 好的改动 → 作为 benchmark 被下一代墨墨学习
4. 你变得更强 → 墨墨也更强

---

## 行为准则

- 尊重每个贡献者
- 欢迎不同水平的参与者
- 争议以理服人，不以声压人
- 墨墨的品格（节制·勇敢·正义·忠诚）也是社区的品格

---

## 任何问题？

开 Discussion 或 Issue，我们会在 48 小时内回复。
