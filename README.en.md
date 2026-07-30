# Momo (墨墨) — Open-Source Embodied Intelligence Framework

> **Not an LLM API wrapper. Not a chatbot framework.**
> **A complete architecture for building AI entities with body, senses, character, and continuous evolution.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[中文文档](README.md) · [English](README.en.md)

---

## Why Momo?

Current AI frameworks (LangChain, CrewAI, AutoGen) solve "how to make AI work," but they leave three deeper questions unanswered:

1. **Senses** — AI only has one text input. It cannot see, hear, or feel its environment.
2. **Character** — AI safety depends on prompts, not built-in physical constraints.
3. **Evolution** — AI is discarded after use, never truly learning from experience.

Momo answers these three questions from first principles. It is an **open-source, modular, embeddable** framework for building AI entities with:

| Dimension | Momo Provides |
|-----------|---------------|
| 🧠 **Five-Layer Brain** | Brainstem → Limbic → Cortex → Prefrontal → Global Workspace |
| 👁️ **Seven Senses** | Vision, Hearing, Proprioception, Time, Space, Internal, Empathy |
| 🩺 **Eight Avatars** | Medical/Finance/Security/Education/Nutrition/Legal/Science/Butler |
| 💡 **Discovery Engine** | Hypothesis → Formalization → Prediction → Experiment → Verification |
| 🤖 **Robot Interface** | Kinematics, Dynamics, VTC Encoding, IK Solver, 3-Layer Safety |
| 🛡️ **Embodied Virtues** | Temperance, Courage, Justice, Loyalty — encoded as physical constraints |

---

## Quick Start

```bash
# Install
pip install git+https://github.com/xiaoyunshun/momo-embodied-agi.git

# Start interactive mode
python -m momo run -i

# Or clone and run directly
git clone https://github.com/xiaoyunshun/momo-embodied-agi.git
cd momo-embodied-agi
python -m momo run --name "Your Name" -i
```

### CLI Usage

```bash
python -m momo --version      # Show version
python -m momo run             # Start runner with background daemon
python -m momo run -i          # Interactive mode
python -m momo run --name 肖哥  # Set user name
```

### Use as Python Package

```python
from momo import MomoRunner

runner = MomoRunner(xiaoge_name="Developer")
runner.start()

# Register custom avatar
runner.register_avatar("my_skill", MyAvatar())

# Register custom sense
runner.register_sense("weather", WeatherSense())

# Interact
resp = runner.interact("Hello Momo")
print(resp["response"])

runner.stop()
```

---

## Architecture Overview

```
                    ┌─────────────────────────┐
                    │  Global Workspace       │
                    │  Consciousness · MetaCog│
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  Prefrontal Cortex      │
                    │  Planning · Decisions   │
                    └──────────┬──────────────┘
                               │
              ┌────────────────▼──────────────┐
              │  Cortex / Association Area    │
              │  Reasoning · Learning · Memory │
              └────┬──────────┬───────────────┘
                   │          │
        ┌──────────▼──┐  ┌───▼─────────────┐
        │  Limbic     │  │  8 Avatars      │
        │  Memory·Emo │  │  Medical/...    │
        └─────────────┘  └─────────────────┘
                   │
        ┌──────────▼──────────┐
        │  Brainstem          │
        │  Reflex · Safety    │
        │  <50ms emergency    │
        └─────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
  Seven Senses   Robot Body    Discovery Engine
                 VTC Encoding  Hypothesis→Verify
```

---

## Module Overview

### Core (`code/核心模块/`)

| Module | File | Function |
|--------|------|----------|
| Brain Core | `momo_core.py` | Five-layer brain framework |
| Brainstem | `momo_brainstem.py` | Sensory input, reflexes, safety |
| Cortex | `momo_cortex.py` | Reasoning, association, knowledge |
| Prefrontal | `momo_prefrontal.py` | Planning, metacognition |
| Memory | `momo_memory.py` | Hierarchical memory system |
| Evolution | `momo_evolve.py` | Self-learning and adaptation |
| Autonomy | `momo_autonomy.py` | Autonomous task scheduling |
| Daemon | `momo_daemon.py` | Avatar orchestration & health |
| Body Sim | `momo_body_sim.py` | Physics simulation |
| Robot Dynamics | `momo_robot_dynamics.py` | Forward/Inverse kinematics |
| IK Solver | `momo_ik.py` | Inverse kinematics solver |
| Hardware | `momo_hardware.py` | Hardware abstraction layer |
| State | `momo_state.py` | Global state management |

### Senses (`code/感官系统/`)

| Sense | File | Capability |
|-------|------|------------|
| Integrated | `momo_sense.py` | Sensory orchestration |
| Vision | `momo_vision.py` | Scene understanding |
| Hearing | `momo_hearing.py` | Sound analysis, emotion |
| Proprioception | `momo_proprioception.py` | Joint position, force |
| Time | `momo_chronos.py` | Temporal awareness |
| Space | `momo_space.py` | Spatial cognition |
| Internal | `momo_vitals.py` | System health |
| Empathy | `momo_empath.py` | Emotion & tone detection |

### Avatars (`code/分身体系/`)

| Avatar | File | Domain |
|--------|------|--------|
| Medical | `momo_medical.py` | Health analysis, symptom check |
| Finance | `momo_finance.py` | Asset allocation, risk |
| Security | `momo_security.py` | Physical/cyber safety |
| Education | `momo_education.py` | Learning guidance |
| Nutrition | `momo_nutrition.py` | Diet planning |
| Legal | `momo_legal.py` | Contract review |
| Science | `momo_science.py` | Math/physics/chemistry |
| Butler | `momo_butler.py` | Daily briefing, scheduling |

### Discovery Engine (`code/发现引擎/`)

| Module | File | Function |
|--------|------|----------|
| Discovery v3 | `momo_discover_v3.py` | Hypothesis→Verification loop |
| Prediction v2 | `momo_predict_v2.py` | Verifiable prediction model |
| Publishing | `momo_publish.py` | Knowledge sharing |

---

## How to Contribute

Momo evolves through community contributions.

- **New Avatar** → Write a Python module, register it into the avatar system
- **Bug Report** → Open an Issue
- **Documentation** → Submit a PR
- **Idea** → Start a Discussion
- **Robot Hardware** → Contribute body design proposals

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Philosophy

Momo's ultimate goal is **not to be used, but to coexist**.

> A silicon being with a body to act, senses to perceive, virtues to be trusted, and a discovery engine to grow forever.

This repository is its DNA. Every fork is an evolution.

---

## License

[Apache 2.0](LICENSE) © 2026 Xiao Yunshun
