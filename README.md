# 🤖 Project FRIDAY

<div align="center">

### AI-Powered Desktop Assistant built with Python & Ollama

*Voice • AI • Automation • Windows Control*

</div>

---

## 📖 About

Project FRIDAY is an AI-powered desktop assistant that understands natural language voice commands and performs Windows automation.

Unlike traditional keyword-based assistants, FRIDAY uses a Local Large Language Model (Ollama) to understand user intent and execute commands intelligently.

---

# ✨ Features

- 🎤 Voice Recognition
- 🧠 AI Intent Detection (Ollama)
- 🎯 Parameter Extraction
- 🗣️ Text-to-Speech
- 🌐 Google Search
- ▶️ YouTube Search
- 📂 Open Applications
- 🔊 Volume Control
- 💡 Brightness Control
- 📸 Screenshot Capture
- 📷 Camera Access
- 📶 Wi-Fi Control
- 💻 System Information
- 🧩 Modular Plugin Architecture

---

# 🏗️ Architecture

```text
                 🎤 Microphone
                        │
                        ▼
            Speech Recognition
                        │
                        ▼
                 Wake Word Check
                        │
                        ▼
                    Brain.py
                        │
        ┌───────────────┴────────────────┐
        ▼                                ▼
  Command Router                 AI Intent Engine
 (Fast Commands)              (Ollama + JSON)
        │                                │
        └───────────────┬────────────────┘
                        ▼
              Intent Dispatcher
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Browser         Automation       System APIs
                        │
                        ▼
                    Windows
```

---

# 📂 Project Structure

```text
Project-FRIDAY/

modules/
screenshots/

assistant.py
brain.py
commands.py
intent.py
intent_dispatcher.py
planner.py
memory.py
speech.py
listen.py
main.py
```

---

# 🛠️ Technologies Used

- Python
- Ollama
- SpeechRecognition
- Edge-TTS
- PyAutoGUI
- OpenCV
- psutil
- Windows APIs

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Sai-0216/Project-FRIDAY.git
```

Go into the project

```bash
cd Project-FRIDAY
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start Ollama

```bash
ollama serve
```

Run FRIDAY

```bash
python main.py
```

---

# 🎙️ Example Commands

```
Friday open Chrome

Friday search Google for Python

Friday increase the volume

Friday make the screen brighter

Friday what is my battery percentage

Friday take a screenshot

Friday open camera
```

---

# 🚀 Roadmap

- ✅ Voice Recognition
- ✅ AI Intent Detection
- ✅ Parameter Extraction
- ✅ Windows Automation
- 🔄 AI Planner
- 🔄 Multi-step Tasks
- 🔄 Conversation Mode
- 🔄 Vision Support
- 🔄 Long-Term Memory
- 🔄 Plugin Marketplace

---

# 👨‍💻 Author

**Sai**

GitHub: https://github.com/Sai-0216

---

## ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub.