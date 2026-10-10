# OMNI-AI — Intelligent Cross-Platform Assistant

A powerful AI assistant with a futuristic web UI, real-time system monitoring, voice capabilities, and end-to-end encryption.

---

## 🚀 Quick Start (Windows)

> **No command-line knowledge required.**

1. **Download** the `OMNI-AI` folder
2. **Double-click** `START_OMNI_AI.bat`
3. Your browser opens at `http://localhost:5000` — done.

On first run the launcher automatically installs the required packages.

---

## 🛠 Manual Setup

```bat
# First-time setup (installs dependencies)
install.bat

# Start the app
python app.py
```

### Optional — enable AI model, voice & more

```bat
pip install -r requirements-optional.txt
```

---

## 📁 Project Structure

```
OMNI-AI/
├── START_OMNI_AI.bat       ← double-click launcher
├── install.bat             ← first-time setup
├── app.py                  ← primary entry point
├── main.py                 ← CLI entry point
├── requirements.txt        ← required (auto-installed)
├── requirements-optional.txt
│
├── core/                   ← AI brain
│   ├── brain.py            ← intent classification, transformer model
│   ├── memory.py           ← conversation context
│   ├── personality.py      ← response generation
│   └── ai_models.py        ← TF / PyTorch model wrappers
│
├── hardware/               ← device control (flashlight, camera, volume…)
├── voice/                  ← STT / TTS engines
├── security/               ← encryption, password hashing, audit
├── platforms/              ← app launcher / controller
├── integration/            ← wires all modules together
│
└── ui/                     ← futuristic web interface
    ├── index.html
    ├── styles.css
    └── script.js
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web UI |
| POST | `/api/chat` | Send a message to the AI brain |
| GET | `/api/status` | Brain availability |
| GET | `/api/health` | Live CPU / memory / disk |
| GET | `/api/capabilities` | Installed feature flags |

### Example — chat with the brain

```bash
curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "turn on the flashlight"}'
```

---

## ⚙ Architecture

OMNI-AI follows **SOLID** principles:

- **Single Responsibility** — each class has exactly one job
- **Open/Closed** — extend features without modifying core logic
- **Liskov Substitution** — PyTorch / TensorFlow / Mock models are interchangeable
- **Interface Segregation** — modules expose only what callers need
- **Dependency Inversion** — high-level modules depend on abstractions

### Feature availability

| Feature | Required package |
|---------|-----------------|
| Web UI + chat | *(built-in)* |
| System monitoring | `psutil` |
| Encryption | `cryptography` |
| PyTorch transformer model | `torch` |
| TensorFlow model | `tensorflow` |
| Text-to-speech | `pyttsx3` |
| Speech recognition | `SpeechRecognition` + `pyaudio` |
| Windows WMI monitoring | `WMI` + `PyWin32` |

---

## 📝 CLI Usage

```bash
# Interactive chat
python main.py

# One-shot command
python main.py "open whatsapp"

# Web server with options
python app.py --port 8080 --no-browser --debug
```

---

## License

MIT