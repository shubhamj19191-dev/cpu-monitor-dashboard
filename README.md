# CPU Monitor Pro

A premium PySide6 desktop dashboard for realtime CPU, memory, temperature, boot time, process, and per-core activity monitoring.

## Features

- Modern frameless desktop window
- Animated premium gradient background
- Realtime CPU gauge and status card
- Live CPU trend graph
- Per-core activity bars
- Memory, temperature, frequency, and boot-time cards
- Generated app icon at runtime

## Run

```powershell
pip install -r requirements.txt
python main.py
```

## Build A Windows App

```powershell
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "CPU Monitor Pro" main.py
```

The app will be created inside the `dist` folder.
