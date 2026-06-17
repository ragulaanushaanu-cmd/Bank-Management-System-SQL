from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
class UserLogin(BaseModel):
    email: str
    password: str
class AccountCreate(BaseModel):
    user_id: int
    acc_type: str
class AccountResponse(BaseModel):
    acc_id: int  # <-- MAKE SURE THIS LINE EXISTS
    user_id: int
    acc_type: str
    balance: float

    class Config:
        from_attributes = True
class DepositRequest(BaseModel):
    acc_id: int
    amount: float
class WithdrawRequest(BaseModel):
    acc_id: int
    amount: float
class TransferRequest(BaseModel):
    sender_acc: int
    receiver_acc: int
    amount: float
class LoanRequest(BaseModel):
    user_id: int
    amount: float