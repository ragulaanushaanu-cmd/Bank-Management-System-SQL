from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)

class Account(Base):
    __tablename__ = "accounts_api"

    acc_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    acc_type = Column(String(20))

    balance = Column(Float, default=0)


class Transaction(Base):
    __tablename__ = "transactions_api"

    id = Column(Integer, primary_key=True, index=True)

    acc_id = Column(Integer, ForeignKey("accounts_api.acc_id"))

    transaction_type = Column(String(20))

    amount = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


class Loan(Base):
    __tablename__ = "loans_api"

    loan_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    amount = Column(Float)

    status = Column(String(20))