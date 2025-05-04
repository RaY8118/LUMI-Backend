# 🧠 Lumi Alzheimer's and Elderly Care App - Backend (Flask API)

This repository contains the **backend code** for the **LUMI Alzheimer's and Elderly Care App** 🧓👵. The backend powers all the core features such as **reminders**, **face recognition**, **object detection**, **location tracking**, **real-time chat**, and **AI chatbot support**. It is built using **Flask** and integrates with **MongoDB**, **WebSocket**, and **AI models** for intelligent support.

---

## ✨ Features

### 1. 📝 Reminders API
- 📌 Create, update, retrieve, and delete reminders.
- ⚠️ Tag reminders as *urgent* or *important*.
- 🔔 Notifications triggered for scheduled reminders.

### 2. 📸 Face Recognition API
- 👤 Identifies familiar faces using the `face_recognition` Python library.
- 📥 Accepts image input and returns recognition results.

### 3. 🔍 Object Detection API
- 🤖 Detects common household or personal objects using YOLO.
- 🏷️ Returns labels for detected objects from uploaded images.

### 4. 🌍 Location Tracking API
- 📍 Tracks and stores users’ live location updates.
- 🧭 Allows caregivers to monitor patient movements and receive alerts.

### 5. 💬 Real-time Chatroom (Flask-SocketIO)
- 🧑‍🤝‍🧑 Enables communication between caregivers and patients.
- 🔐 Secured using unique userID-based authentication and rooms.
- 📨 Integrated with Expo push notifications for urgent messages.

### 6. 🤖 Chatbot Support
- 🧠 Provides a built-in assistant to help elderly users perform tasks or answer questions.
- 🗣️ Accessible via the chat interface to enhance user experience.

---

## ⚙️ Technology Stack

- 🔙 **Flask** — REST API and Socket.IO support
- 🧠 **face_recognition** — Face detection and recognition
- 🕵️ **YOLO** — Object detection
- 📦 **MongoDB** — NoSQL database
- 🌐 **Flask-SocketIO** — Real-time bi-directional chat
- ✨ **Gemini / Custom AI model** — For chatbot capabilities
- 🔐 **Expo Push Notifications** — For caregiver alerts and reminders

---

## 🚀 Getting Started

### 📋 Prerequisites
- 🐍 Python 3.x
- 📦 Flask & Flask-SocketIO
- 🗄️ MongoDB
- 📷 YOLO model setup
- 💬 Expo push notification token setup

### 🔧 Installation

```bash
git clone https://github.com/RaY8118/LUMI-Backend.git
cd LUMI-Backend

python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

pip install -r requirements.txt
```
### ⚙️ Configuration

* Create a `.env` file for database credentials, secret keys, and token configs.
* Set up YOLO model weights and config as per their documentation.

### ▶️ Run the server

```bash
python run.py
```

---

## 📡 API Endpoints

### 📝 Reminders

* `GET /reminders`
* `POST /reminders`
* `PUT /reminders/:id`
* `DELETE /reminders/:id`

### 📸 Face Recognition

* `POST /detect_faces`

### 🔍 Object Detection

* `POST /detect_object`

### 🌍 Location Tracking

* `POST /location`

### 💬 Chatroom

* WebSocket Endpoint: `/chatroom`
* Custom events for joining rooms, sending messages, and disconnecting

### 🤖 Chatbot

* `POST /assistant`: Send a message to the AI assistant and receive a response

---

## 🛠️ YOLO Model Setup

* Download weights (e.g. `yolov10b.pt`) and config files.
* Store them in a `/model` folder and load them via your object detection service.

---


### 📂 Folder Structure

* **`/app`**: Contains the core logic for features like reminders, location tracking, chat, and more. This includes the implementation of Flask Blueprints for modular API handling.

* **`/config`**: Holds the configuration settings for the application, including environment-specific variables and app settings.

* **`/uploads`**: Stores user-uploaded files, such as profile images or other media for the app.


---

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to GitHub (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for full details.
