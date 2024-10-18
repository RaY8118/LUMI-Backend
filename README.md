# 🧠 Lumi Alzheimer's and Elderly Care App - Backend (Flask API)

This repository contains the backend code for the **Alzheimer's and elderly care application** 🧓👵, which provides **API endpoints** for various features like reminders, face recognition, object detection, and location tracking. The backend is built using **Flask** and integrates with **MongoDB** for data storage.

## ✨ Features

### 1. 📝 **Reminders API**
   - 📌 Endpoints for creating, updating, retrieving, and deleting reminders.
   - ⚠️ Reminders are tagged as urgent or important based on user input.

### 2. 📸 **Face Recognition API**
   - 👤 Built using the `face_recognition` Python library to help identify familiar faces.
   - 📥 Processes images and returns the recognition results via the API.

### 3. 🔍 **Object Detection API**
   - 🤖 Powered by a YOLO (You Only Look Once) model for object detection.
   - 🏷️ Identifies and labels objects from images provided by the user.

### 4. 🌍 **Location Tracking API**
   - 📍 Provides endpoints to track and update the user's location, which can be shared with caregivers.

## ⚙️ Technology Stack

- 🚀 **Flask**: Web framework for creating the RESTful API.
- 🗄️ **MongoDB**: Database for storing user data, reminders, and other information.
- 🧑‍🤝‍🧑 **face_recognition**: Python library used for implementing face recognition features.
- 📷 **YOLO Model**: Used for object detection, recognizing multiple objects in images.

## 🚀 Getting Started

### 📋 Prerequisites
- 🐍 [Python 3.x](https://www.python.org/downloads/)
- 🧪 [Flask](https://flask.palletsprojects.com/)
- 🗄️ [MongoDB](https://www.mongodb.com/)
- 🧑‍🤝‍🧑 [face_recognition](https://pypi.org/project/face-recognition/)
- 🔍 YOLO Model setup for object detection

### 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RaY8118/LUMI-Backend.git
   cd LUMI-Backend
   ```

2. **Set up a virtual environment and activate it**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your MongoDB connection and any necessary environment variables in the `.env` file.**

5. **Run the Flask development server**:
   ```bash
   python3 run.py
   ```

## 🔗 API Endpoints

### 📝 **Reminders**
- **GET /reminders**: Fetch all reminders
- **POST /reminders**: Create a new reminder
- **PUT /reminders/:id**: Update an existing reminder
- **DELETE /reminders/:id**: Delete a reminder

### 📸 **Face Recognition**
- **POST /recognize-face**: Upload an image for face recognition

### 🔍 **Object Detection**
- **POST /detect-object**: Upload an image for object detection using YOLO

### 🌍 **Location Tracking**
- **POST /location**: Update or track the user's current location

## 🛠️ YOLO Model Setup

You'll need to download and set up the **YOLO model weights and configuration** for object detection. Refer to the official YOLO documentation for setup instructions.

## 🤝 Contributing

1. **Fork the project**
2. **Create your feature branch** (`git checkout -b feature/YourFeature`)
3. **Commit your changes** (`git commit -m 'Add some YourFeature'`)
4. **Push to the branch** (`git push origin feature/YourFeature`)
5. **Open a pull request**

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
