# ✈️ ATLAS: Intelligent Air Traffic Control Dashboard

## Overview

**ATLAS** is an AI-powered air traffic control dashboard designed to enhance situational awareness, automate runway allocation, and improve communication reliability. By combining real-time fatigue monitoring, intelligent decision support, and speech-to-text capabilities, ATLAS empowers controllers and pilots to operate safely and efficiently.

---

## ✨ Key Features

- **Runway Allocation Automation**
  - Dynamically assigns runways based on traffic, schedules, and priority rules.
- **Real-Time Fatigue Monitoring**
  - Detects fatigue in pilots and controllers using machine learning models.
- **Integrated Communication**
  - Converts radio commands to text and supports chat-based coordination.
- **Centralized Dashboard**
  - Provides a consolidated view of air traffic, fatigue status, and communication logs.

---

## ⚙️ Tech Stack

| Component            | Technology                          |
|----------------------|-------------------------------------|
| **Backend**          | Python, Flask                      |
| **Frontend**         | HTML, CSS, JavaScript              |
| **Machine Learning** | TensorFlow, OpenCV, Mediapipe      |
| **Speech Processing**| Whisper, SpeechRecognition         |
| **Data Handling**    | Pandas, NetworkX                   |
| **Visualization**    | Matplotlib, Tkinter                |

---

## 📂 Project Structure

.
├── app.py # Flask API endpoint
├── Runway_simulation.py # Runway allocation and visualization
├── fatigue_detection.py # Real-time fatigue monitoring
├── 2_way_comm_voicebridge.py # Audio transcription and NLP analysis
├── notifier.py # WebSocket notifications
├── run_server.py # WebSocket server
├── templates/
│ └── index.html # Frontend interface
└── static/ # CSS, JS, media files

## 🧠 How It Works

### Fatigue Detection
Captures video using OpenCV and Mediapipe to detect blinks, yawns, and face-touching behavior. Computes fatigue scores and raises alerts.

### Runway Allocation
Prioritizes flights based on emergency status, fuel level, and aircraft size. Visualizes landing sequences using Matplotlib animations.

### Communication Monitoring
Records or ingests pilot and ATC audio. Transcribes speech to text using Whisper. Analyzes instructions and potential misunderstandings.

### WebSocket Notifications
Sends real-time alerts to connected clients.

---

## ✨ Future Enhancements

- Cloud deployment and scaling
- Multi-user authentication
- Integration with live radar feeds
- Advanced NLP for richer communication analysis
- Real-time weather data integration

---

## 🙏 Acknowledgments

Special thanks to the open-source community and libraries that made this project possible.
