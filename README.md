# 🏦 Bank Management System API

A FastAPI-based Bank Management System API with JWT Authentication, User Management, and Banking Operations like Deposit, Withdraw, and Transaction Tracking.

---
## 🚀 Overview
This project is a beginner-friendly backend API for banking operations built using FastAPI and MySQL.
# ✨ Features

## 🔐 Authentication
- User Registration
- User Login
- JWT Token Authentication
- Password Hashing using bcrypt

## 👤 User Features
- View Account Details
- Deposit Money
- Withdraw Money
- View Transaction History
- Check Balance

## 🏦 Banking Features
- Create Bank Account
- Update Account Details
- Transaction Tracking
- Secure Balance Management

---

# 🧰 Tech Stack
- Python
- FastAPI
- SQLAlchemy
- MySQL
- JWT Authentication
- Passlib (bcrypt)
- Pydantic

---

📁 Project Structure
main.py → Entry point
models.py → Database models
schemas.py → Request/response validation
auth.py → Authentication logic
security.py → Password hashing & JWT
database.py → Database connection
requirements.txt → Dependencies

---

# ⚙️ Installation

## Clone Repository
```bash
git clone https://github.com/ragulaanushaanu-cmd/Bank-Management-System-SQL.git
cd Bank-Management-System-SQL
python -m venv .venv
.venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
Configure Database

Create .env file:

DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bank_db

SECRET_KEY=your_secret_key
ALGORITHM=HS256

Run Project
uvicorn main:app --reload
🌐 API URLs
Home: http://127.0.0.1:8000
Swagger Docs: http://127.0.0.1:8000/docs
🔗 API Endpoints
Authentication
Method	Endpoint
POST	/register
POST	/login
Banking
Method	Endpoint
POST	/deposit
POST	/withdraw
GET	/balance
GET	/transactions
User
Method	Endpoint
GET	/profile
PUT	/profile
📊 Example Response
{
  "account_number": 101,
  "balance": 5000,
  "status": "active"
}
👨‍💻 Author

Anusha Ragula
Backend Developer | Python | FastAPI | MySQL
