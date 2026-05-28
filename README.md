<div align="center">

# 💰 Budget Tracker

**A cute little web app to keep your finances happy and healthy!**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)

</div>

---

## ✨ What it does

Budget Tracker is a simple, full-stack personal finance app that helps you:

- 📥 **Log income** — track every paycheck, freelance gig, or side hustle
- 📤 **Track expenses** — see exactly where your money goes
- 🗂️ **Organize by category** — food, rent, fun, etc.
- 📊 **View a dashboard summary** — get a birds-eye view of your balance at a glance
- 🔐 **Keep it private** — each user has their own secure account

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Templates | Jinja2 |
| Database | SQLite |
| Auth | bcrypt + signed session cookies |
| Containerization | Docker (multi-stage build) |

---

## 🚀 Getting Started

### Option 1 — Run locally with Python

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn app.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser. 🎉

---

### Option 2 — Run with Docker 🐳

```bash
# Build the image
docker build -t budget-tracker .

# Run it
docker run -p 8000:8000 -v budget_data:/home/appuser/app/data budget-tracker
```

App will be live at [http://localhost:8000](http://localhost:8000).

---

## 📁 Project Structure

```
budget_tracker/
├── app/
│   ├── main.py          ← FastAPI app entry point
│   ├── auth.py          ← Authentication helpers
│   ├── database.py      ← SQLite connection & init
│   ├── models.py        ← Pydantic data models
│   └── routes/
│       ├── auth.py      ← Register & login endpoints
│       ├── transactions.py ← Income/expense CRUD API
│       └── pages.py     ← HTML page routes
├── templates/
│   ├── dashboard.html   ← Main dashboard view
│   ├── login.html       ← Login page
│   └── register.html    ← Registration page
├── static/
│   ├── css/style.css    ← Styles
│   └── js/dashboard.js  ← Dashboard interactivity
├── Dockerfile
└── requirements.txt
```

---

## 🔒 Security Highlights

- Passwords are hashed with **bcrypt** — never stored in plain text
- Sessions use **signed cookies** via `itsdangerous`
- Docker container runs as a **non-root user**
- All transaction endpoints require authentication

---

## 💡 How to Use

1. **Register** a new account at `/register`
2. **Log in** at `/login`
3. Add your first **income** or **expense** from the dashboard
4. Watch your **balance update** in real time ✨

---

<div align="center">

Made with 💖 and Python

</div>
