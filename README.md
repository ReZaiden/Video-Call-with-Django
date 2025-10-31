# 🎥 Django Video Call App with WebRTC

![Django](https://img.shields.io/badge/Django-5.2-brightgreen)
![Channels](https://img.shields.io/badge/Channels-4.0-blue)
![WebRTC](https://img.shields.io/badge/WebRTC-RealTime-orange)
![Redis](https://img.shields.io/badge/Redis-ChannelLayer-red)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

A **real-time peer-to-peer video calling** web application built using **Django**, **Django Channels**, **WebRTC**, and **Redis**.  
Users can make and receive video calls, manage their call history, and enjoy a modern, responsive UI inspired by **WhatsApp**.

> ⚠️ **Note:** This project is designed for development and testing.  
> For production deployment, make sure to configure **HTTPS**, **secure WebSockets**, and a **TURN server** for reliable connectivity.

---

## 🚀 Features

- 🔄 Real-time **two-way video calling** (WebRTC)
- 📡 **WebSocket** signaling via Django Channels
- 📞 **Call state management:** `RINGING`, `CONNECTED`, `MISSED`, `ENDED`
- 👥 Simple **login & signup** system
- 🕒 **Call history** with timestamps and duration
- 🎛️ **In-call controls:** mute, disable camera, end call
- ✨ Animated **incoming call modal**
- 📱 **Responsive UI**, inspired by WhatsApp
- ⚡ **Redis-backed Channel Layer** for real-time communication

---

## 🧠 Tech Stack

| Technology       | Version   | Description |
|------------------|-----------|--------------|
| **Django**       | 5.2       | Web framework |
| **Django Channels** | 4.0+   | WebSocket and async support |
| **Redis**        | 6.0+      | Channel layer backend |
| **WebRTC**       | Native    | Real-time audio/video streaming |
| **JavaScript**   | Vanilla   | Frontend logic |
| **HTML/CSS**     | Custom    | UI design |

---

## ⚙️ Prerequisites

Before running the project, make sure you have:

- 🐍 **Python 3.9+**
- 📦 **pip** (Python package manager)
- 🔴 **Redis Server** (running locally or via Docker)
- 🌐 **Git**

You can install Redis via Docker easily:

```bash
docker run -d -p 6379:6379 redis
```

---

## 🛠️ Installation

Clone the repository and set up the environment:

```bash
# Clone the project
git clone https://github.com/ReZaiden/Video-Call-with-Django.git
cd Video-Call-with-Django

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # On Linux/Mac
venv\Scripts\activate         # On Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start Redis (if not already running)
redis-server
```

---

## ▶️ Run the Project

```bash
# Collect Static files
python manage.py collectstatic

# Push to database
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start Django server
daphne -b 127.0.0.1 -p 8000 project.asgi:application

Then open your browser and go to:
http://127.0.0.1:8000
```

---

## 📡 How It Works

1. **Sign in or create an account**  
2. **Enter a username** to call another registered user  
3. The receiver sees an **incoming call modal**  
4. Both users are connected via **WebRTC peer connection**  
5. Media streams (audio/video) are exchanged **P2P**  
6. **Signaling** handled through **Django Channels (WebSockets)**  
7. **Redis** manages real-time message passing

---

```

## 🧩 Project Structure

```plaintext
├── project/
│   ├── asgi.py               # ASGI entry point (for WebSockets)
│   ├── settings.py           # Django + Channels configuration
│   └── urls.py               # URL routing
│
├── VideoCall/
│   ├── consumers.py          # WebSocket consumers for signaling
│   ├── routing.py            # Channel routing setup
│   ├── models.py             # Call and user models
│   ├── views.py              # Authentication and view logic
│   ├── templates/            # HTML templates
│   ├── static/js/main.js     # WebRTC and signaling logic
│   ├── static/js/login.js    # JS of login page
│   ├── static/css/style.css  # CSS of main page
│   └── static/css/login.css  # CSS of login page
│
├── requirements.txt
└── manage.py
```

---

## 🔒 Security Notes

- Use **HTTPS** in production (WebRTC requires secure contexts)
- Add a **TURN server** for NAT traversal
- Configure proper **CORS and CSRF settings**
- Consider **JWT authentication** for scalable setups

---

## 💡 Future Improvements

- ✅ TURN/STUN server integration  
- ✅ Typing & chat support during calls  
- ✅ Push notifications for missed calls  
- ✅ Dark & light theme toggle  
- ✅ Docker Compose setup for deployment  

---

## 🧑‍💻 Author

**Developed by:** ReZaiden 
💼 **GitHub:** [@ReZaiden](https://github.com/ReZaiden)  
📧 **Contact:** rezaidensalmani@gmail.com  

---

## 🪪 License

This project is licensed under the **MIT License**.
