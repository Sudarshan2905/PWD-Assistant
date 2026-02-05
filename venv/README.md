# PWD Assistant 🧑‍🦽💙

PWD Assistant is a **Flask + MySQL based web application** designed to support **Persons With Disabilities (PWD)** and **NGOs** by providing secure authentication, role-based dashboards, profile management, and NGO student tracking features.

This project follows **industry-level backend practices** such as environment variables, password hashing, session handling, and cloud deployment readiness.

---

## 🚀 Features

### 👤 User (Individual)
- Secure signup & login
- Password hashing using bcrypt
- Profile view & update
- Access to services, resources, and community pages

### 🏢 NGO
- Role-based login (NGO vs Individual)
- NGO dashboard
- Manage students (Add / Update / Delete)
- REST API endpoints for student management

### 🔐 Security
- Hashed passwords (bcrypt)
- Session-based authentication
- Environment variables for secrets
- Role-based route protection

---

## 🛠️ Tech Stack

| Layer | Technology |
|-----|-----------|
Backend | Flask (Python) |
Database | MySQL |
Authentication | bcrypt |
Frontend | HTML, CSS, Jinja2 |
Deployment | Gunicorn, Render |
Database Hosting | Railway (Cloud MySQL) |
Version Control | Git & GitHub |

---

## 📁 Project Structure
backend/
│── app.py
│── requirements.txt
│── Procfile
│── .gitignore
│── templates/
│── static/


---

## ⚙️ Environment Variables

The application uses **environment variables** for security.

### Required Variables
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
DB_PORT
SECRET_KEY


For local development, these are loaded using a `.env` file.

---

## 🧪 Local Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/pwdassistant.git
cd pwdassistant

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup MySQL Database
CREATE DATABASE pwd_assistant;


Create users table:

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    user_type ENUM('individual', 'ngo') DEFAULT 'individual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

5️⃣ Run Application
python app.py


Open browser:

http://localhost:5000

🌐 Deployment

Backend Hosting: Render

Database: Railway MySQL

Production Server: Gunicorn

The app is fully cloud-deployment ready using environment variables.

📌 API Endpoints (NGO)
Method	Endpoint	Description
GET	/api/students	Fetch NGO students
POST	/api/students	Add new student
PUT	/api/students/<id>	Update student
DELETE	/api/students/<id>	Delete student
🎯 Learning Outcomes

Flask backend development

MySQL database integration

Authentication & authorization

Environment variables & security

Cloud deployment workflow

Real-world debugging & error handling

👨‍💻 Author

Sudarshan Herwade
3rd Year Electronics Engineering Student
Aspiring Software Engineer
Learning Full Stack Development & Cloud Computing

⭐ If you like this project

Give it a ⭐ on GitHub!


---
