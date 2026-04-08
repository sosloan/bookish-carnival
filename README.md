# 🚀 NASA UFO — NASA Space Exploration Agent

> A **Microsoft UFO**-inspired agent framework for exploring NASA data and space missions.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![NASA API](https://img.shields.io/badge/NASA-Open%20APIs-red)](https://api.nasa.gov)

---

## 🌌 Overview

**NASA UFO** (Universal Flight Operations) is an AI-powered agent framework inspired by [Microsoft UFO](https://github.com/microsoft/UFO) that automates the exploration of NASA's open data. Just as UFO agents navigate Windows UIs, NASA UFO agents navigate the cosmos — querying astronomical data, tracking near-Earth objects, browsing Mars rover images, and more.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NASA UFO Framework                       │
│                                                             │
│  ┌──────────────┐     ┌──────────────┐    ┌─────────────┐  │
│  │  HostAgent   │────▶│  MissionAgent│───▶│  NASA Tools │  │
│  │  (Planner)   │     │  (Executor)  │    │  (APIs)     │  │
│  └──────────────┘     └──────────────┘    └─────────────┘  │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│   Route missions       Execute tasks       Fetch data       │
│   Manage state         Use tools           Return results   │
└─────────────────────────────────────────────────────────────┘
```

## 🛸 Features

- 🌠 **Astronomy Picture of the Day (APOD)** — Fetch NASA's daily cosmic image with description
- ☄️ **Near-Earth Object (NEO) Tracker** — Monitor asteroids and comets approaching Earth
- 🔴 **Mars Rover Photos** — Browse images from Curiosity, Opportunity, and Spirit
- 🌍 **Earth Imagery** — Satellite imagery of Earth locations via NASA Earth API
- 🤖 **Agent Pipeline** — UFO-style HostAgent + MissionAgent dual-agent architecture
- 📋 **Mission Memory** — Agents maintain context across multi-step explorations

## 📦 Installation

```bash
git clone https://github.com/sosloan/bookish-carnival
cd bookish-carnival
pip install -r requirements.txt
```

## 🔑 Configuration

Get your free NASA API key at [https://api.nasa.gov](https://api.nasa.gov).

```bash
export NASA_API_KEY="your_api_key_here"
# Or use the demo key (rate-limited):
export NASA_API_KEY="DEMO_KEY"
```

## 🚀 Quick Start

```bash
# Interactive mode
python main.py

# Single mission
python main.py --mission "Show me today's astronomy picture"
python main.py --mission "Find asteroids passing Earth this week"
python main.py --mission "Get Mars rover photos from Curiosity"

# List available tools
python main.py --list-tools
```

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📡 Available NASA Tools

| Tool | Description |
|------|-------------|
| `apod` | Astronomy Picture of the Day |
| `neo` | Near-Earth Object tracking |
| `mars_photos` | Mars Rover photo browser |
| `earth_imagery` | Earth satellite imagery |
| `epic` | Earth Polychromatic Imaging Camera |

## 🏗️ Project Structure

```
bookish-carnival/
├── main.py                  # CLI entry point
├── requirements.txt         # Dependencies
├── nasa_ufo/
│   ├── __init__.py
│   ├── agent.py             # HostAgent + MissionAgent
│   ├── tools.py             # NASA API tool implementations
│   └── config.py            # Configuration management
└── tests/
    ├── __init__.py
    ├── test_agent.py
    └── test_tools.py
```

## 🌟 Inspired By

- [Microsoft UFO](https://github.com/microsoft/UFO) — UI-Focused Operations agent framework
- [NASA Open APIs](https://api.nasa.gov) — Free public APIs from NASA

---

*"That's one small step for an agent, one giant leap for agent-kind."* 🌙
