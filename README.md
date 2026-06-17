# 🏦 Bank Management System API

A FastAPI-based Bank Management System API with JWT authentication and MySQL database.

---

## 🚀 Overview

This is a beginner-friendly backend project for banking operations using FastAPI and MySQL.

---

## ✨ Features

### Authentication
- User Registration
- User Login
- JWT Authentication
- Password Hashing

### User Features
- View Account Details
- Deposit Money
- Withdraw Money
- View Transactions
- Check Balance

### Banking Features
- Create Bank Account
- Update Account
- Transaction Tracking
- Secure Balance Handling

---

## 🧰 Tech Stack
- Python
- FastAPI
- MySQL
- SQLAlchemy
- JWT
- Passlib (bcrypt)

---

## 📁 Project Structure

- main.py → Entry point
- models.py → Database models
- schemas.py → Validation
- auth.py → Login/Register logic
- security.py → Password hashing + JWT
- database.py → DB connection
- requirements.txt → Dependencies

---

## ⚙️ Installation

Clone repo:
git clone https://github.com/ragulaanushaanu-cmd/Bank-Management-System-SQL.git

cd Bank-Management-System-SQL

Create virtual environment:
python -m venv .venv
.venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Run server:
uvicorn main:app --reload

---

## 🌐 API URLs

- Home: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  

---

## 🔗 API Endpoints

### Authentication
- POST /register
- POST /login

### Banking
- POST /deposit
- POST /withdraw
- GET /balance
- GET /transactions

### User
- GET /profile
- PUT /profile

---

## 👨‍💻 Author

Anusha Ragula  
Backend Developer | Python | FastAPI | MySQL
