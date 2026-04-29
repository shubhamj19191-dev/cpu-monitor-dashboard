# CPU Monitor Pro

CPU Monitor Pro is a polished PySide6 desktop app for realtime system monitoring. It shows CPU load, per-core activity, memory usage, estimated temperature, boot time, and a live trend graph inside a modern frameless desktop UI.

## Highlights

- Premium frameless desktop interface
- Animated multicolor gradient background
- Realtime CPU usage gauge
- Live CPU health/status card
- CPU trend graph with smooth updates
- Per-core activity bars
- Frequency, memory, temperature, and boot-time metric cards
- Runtime-generated app icon
- Clean Python-only desktop stack

## Tech Stack

- Python
- PySide6
- psutil
- plyer
- WMI on Windows, when available


## Project Structure

```text
cpu-monitor-dashboard/
|-- main.py              # App entry point
|-- ui.py                # PySide6 desktop UI
|-- Cpu.py               # System monitoring logic
|-- requirements.txt     # Python dependencies
|-- README.md            # Project documentation
`-- .gitignore
```

## Notes

- CPU and memory readings come from `psutil`.
- Temperature support depends on the system. If a direct sensor is not available, the app uses a CPU-load-based estimate.
- The app is designed as a desktop application, not a web dashboard.

## Author

Made by [Shubham](https://github.com/shubhamj19191-dev).
