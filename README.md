# 🏃 HabitFlow

[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://www.python.org/) 
[![Flask](https://img.shields.io/badge/flask-2.3-green?logo=flask)](https://flask.palletsprojects.com/) 
[![GitHub Workflow](https://img.shields.io/github/actions/workflow/status/<your-username>/HabitFlow/ci.yml?branch=main&logo=github)](https://github.com/<your-username>/HabitFlow/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

> **HabitFlow** – Your fun and interactive habit tracker. Track, manage, and build healthy habits every day!  

---

## 📌 Table of Contents
- [🌟 Features](#-features)
- [🎨 Demo & Screenshots](#-demo--screenshots)
- [⚡ Installation](#-installation)
- [🧪 Running Tests](#-running-tests)
- [🐳 Docker Instructions](#-docker-instructions)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [💖 Acknowledgements](#-acknowledgements)

---

## 🌟 Features

- ✅ **User Authentication:** Secure signup and login with Flask-Login  
- ✅ **Dashboard:** Clean UI showing all habits and progress  
- ✅ **Add/Edit/Delete Habits:** Easy habit management  
- ✅ **Progress Tracking:** Visual indicators and streaks  
- ✅ **Responsive Design:** Mobile-friendly and desktop-ready  
- ✅ **CI/CD Ready:** Tested and Docker-ready for deployment  

---

## 🎨 Demo & Screenshots

### 🖼 GIF Demo
![HabitFlow Demo](docs/screenshots/demo.gif)

### 📊 Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### ➕ Add Habit
![Add Habit](docs/screenshots/add_habit.png)

### 📋 Habit List
![Habit List](docs/screenshots/habit_list.png)

---

## ⚡ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/HabitFlow.git
cd HabitFlow

2️⃣ Create a virtual environment

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3️⃣ Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

4️⃣ Setup environment variables

Create a .env file in the project root:

SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///habitflow.db  # Or your Postgres URL

5️⃣ Initialize the database

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

6️⃣ Run the app

python run.py

Open http://127.0.0.1:5000

in your browser.
🧪 Running Tests

pytest --tb=short -v

🐳 Docker Instructions
🔧 Build Docker Image

docker build -t habitflow:latest .

🚀 Run Docker Container

docker run -p 5000:5000 habitflow:latest

🤝 Contributing

We welcome contributions!

    Fork the repository

    Create a new branch (git checkout -b feature/my-feature)

    Make your changes

    Commit your changes (git commit -m "Add new feature")

    Push to your branch (git push origin feature/my-feature)

    Open a Pull Request

📄 License

This project is licensed under the MIT License.
See LICENSE

for details.
💖 Acknowledgements

    Flask

Bootstrap

Font Awesome

Inspiration from popular habit-tracking apps