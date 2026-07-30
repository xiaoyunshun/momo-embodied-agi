# Developer Guide

Quick-start guide to the Momo framework — create your own avatars, senses, and applications.

[中文版本](开发者指南.md)

---

## Setup

```bash
git clone https://github.com/xiaoyunshun/momo-embodied-agi.git
cd momo-embodied-agi
pip install -e .
```

## Quick Start

```bash
python -m momo run -i
```

Type anything at the `>>>` prompt. Type `exit` to quit.

---

## Architecture

```
  ┌────────────────────┐
  │  Avatar Layer      │  Domain experts: medical/finance/edu/...
  │  You write here    │
  ├────────────────────┤
  │  Sense Layer       │  Senses: vision/hearing/weather/...
  │  You register here │
  ├────────────────────┤
  │  Runner            │  Heartbeat/scheduling/routing
  │  Framework-provided│
  └────────────────────┘
```

**Flow:**

```
Input → Senses process → Route to best avatar → Response returned
```

---

## Your First Avatar

An avatar = a Python class with `process()` and optionally `help()`.

```python
from momo import MomoRunner


class MyAvatar:
    def process(self, text: str) -> dict:
        return {"response": f"You said: {text}"}

    def help(self) -> dict:
        return {
            "name": "Echo",
            "description": "Echoes your input",
            "capabilities": ["echo"],
        }


runner = MomoRunner()
runner.register_avatar("echo", MyAvatar())
runner.start()
resp = runner.interact("hello")
print(resp["response"])  # → "You said: hello"
runner.stop()
```

---

## Your First Sense

A sense = a Python class with `process()` that returns structured perception data.

```python
class MoodSense:
    def process(self, text: str) -> dict:
        positive = ["good", "great", "happy", "love", "nice"]
        negative = ["bad", "terrible", "hate", "angry", "sad"]
        mood = "neutral"
        for w in positive:
            if w in text.lower(): mood = "positive"; break
        for w in negative:
            if w in text.lower(): mood = "negative"; break
        return {"mood": mood}
```

---

## API Reference

```python
runner = MomoRunner(xiaoge_name="User")

# Register an avatar (auto-routed on interact)
runner.register_avatar("name", avatar_instance)

# Register a sense (auto-processed on interact)
runner.register_sense("name", sense_instance)

# Start (background daemon)
runner.start()

# Interact
resp = runner.interact("your text")

# Status
stats = runner.status()

# Stop
runner.stop()
```

---

## Custom Avatar Response Format

Your `process()` method should return a dict:

| Field | Required | Description |
|-------|----------|-------------|
| `response` | ✅ Yes | String response text |
| `confidence` | ❌ Optional | Float 0-1, higher = preferred on routing |

---

## Running Examples

```bash
python3 examples/01_quickstart.py
python3 examples/02_custom_avatar.py
python3 examples/03_custom_sense.py
python3 examples/04_mining_safety.py
python3 examples/05_health_manager.py
python3 examples/06_financial_advisor.py
```

---

## MCP Integration

Momo Runner can connect to MCP (Model Context Protocol) servers to extend its capabilities. Any MCP server's tools become callable as avatars.

```python
from momo import MomoRunner
from momo.mcp_avatar import MCPAvatar

runner = MomoRunner()

# Connect to MCP server (HTTP or stdio)
mcp = MCPAvatar("weather-api", url="http://localhost:8080/mcp")
mcp.connect()
runner.register_avatar("weather_mcp", mcp)

runner.start()
resp = runner.interact("what's the weather like?")
runner.stop()
```

See `momo/mcp_avatar.py` for details.

---

## Project Structure

```
your-project/
├── my_avatar.py       # Your avatar
├── my_sense.py        # Your sense
└── main.py            # Entry point
```
