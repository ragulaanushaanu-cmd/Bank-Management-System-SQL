from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from auth import hash_password, verify_password
from database import engine, get_db
from models import Base, User, Account, Transaction, Loan
from schemas import (
    UserCreate, UserLogin, AccountCreate, 
    DepositRequest, WithdrawRequest, TransferRequest, LoanRequest
)
from security import create_access_token, verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Bind structural engine models
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bank Management API", version="1.0.0")
security_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload  # This contains {"sub": "user_id"}

@app.get("/")
def home():
    return {"status": "healthy", "message": "Bank Management API Running"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password),
            is_admin=False
    )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User Registered Successfully"
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already registered."
        )

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {"sub": str(db_user.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
# ... right after the @app.post("/login") code block ...

@app.get("/me")
def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == int(current_user["sub"])).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    return {
    "id": user.id,
    "username": user.username,
    "email": user.email
}
@app.post("/create-account")
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if str(account.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: You can only create accounts for your own user ID."
        )

    user_exists = db.query(User).filter(User.id == account.user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    new_account = Account(
        user_id=account.user_id,
        acc_type=account.acc_type,
        balance=0.0
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {
    "message": "Account Created Successfully",
    "account_id": new_account.acc_id,
    "user_id": new_account.user_id,
    "account_type": new_account.acc_type,
    "balance": new_account.balance
}

@app.post("/deposit")
def deposit(
    data: DepositRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than zero"
        )

    account = db.query(Account).filter(Account.acc_id == data.acc_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if str(account.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: You can only deposit into your own accounts."
        )

    account.balance += data.amount
    transaction = Transaction(
        acc_id=account.acc_id,
        transaction_type="Deposit",
        amount=data.amount
    )
    db.add(transaction)
    db.commit()
    return {
        "message": "Deposit Successful",
        "new_balance": account.balance
    }

@app.post("/withdraw")
def withdraw(
    data: WithdrawRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than zero"
        )

    account = db.query(Account).filter(Account.acc_id == data.acc_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if str(account.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: You can only withdraw from your own accounts."
        )

    if account.balance < data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    account.balance -= data.amount
    transaction = Transaction(
        acc_id=account.acc_id,
        transaction_type="Withdraw",
        amount=data.amount
    )
    db.add(transaction)
    db.commit()
    return {
        "message": "Withdrawal Successful",
        "new_balance": account.balance
    }

@app.post("/transfer")
def transfer(
    data: TransferRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than zero"
        )

    if data.sender_acc == data.receiver_acc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer to same account"
        )

    sender = db.query(Account).filter(Account.acc_id == data.sender_acc).first()
    receiver = db.query(Account).filter(Account.acc_id == data.receiver_acc).first()

    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender account not found")
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver account not found")

    if str(sender.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: You can only transfer funds from your own accounts."
        )

    if sender.balance < data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    sender.balance -= data.amount
    receiver.balance += data.amount

    sender_transaction = Transaction(
        acc_id=sender.acc_id,
        transaction_type="Transfer Out",
        amount=data.amount
    )
    receiver_transaction = Transaction(
        acc_id=receiver.acc_id,
        transaction_type="Transfer In",
        amount=data.amount
    )
    db.add(sender_transaction)
    db.add(receiver_transaction)
    db.commit()
    return {"message": "Transfer Successful"}

@app.get("/account/{acc_id}")
def get_account(
    acc_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.acc_id == acc_id).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if str(account.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    return {
        "acc_id": account.acc_id,
        "user_id": account.user_id,
        "acc_type": account.acc_type,
        "balance": account.balance
    }
@app.get("/transactions/{acc_id}")
def transaction_history(
    acc_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    account_exists = db.query(Account).filter(
        Account.acc_id == acc_id
    ).first()

    if not account_exists:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    # ADD THIS HERE
    if str(account_exists.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.acc_id == acc_id)
        .order_by(Transaction.id.desc())
        .all()
    )

    return [
    {
        "id": t.id,
        "transaction_type": t.transaction_type,
        "amount": t.amount,
        "created_at": t.created_at
    }
    for t in transactions
]

@app.post("/loan")
def apply_loan(
    loan: LoanRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if loan.amount <= 0:
        raise HTTPException(status_code=400, detail="Loan amount must be positive")

    if str(loan.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: You can only apply for a loan under your own user ID."
        )

    user_exists = db.query(User).filter(User.id == loan.user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    new_loan = Loan(
        user_id=loan.user_id,
        amount=loan.amount,
        status="Pending"
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return {
        "message": "Loan Application Submitted",
            "loan_id":new_loan.loan_id
    }
# TODO: Restrict to admin users
# TODO: Restrict to admin users
@app.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Mocking admin role check via sub string for demonstration 
    # If not admin, explicitly block before processing query
    if current_user.get("sub") != "1":  # Assuming '1' is admin ID, adjust as needed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
        
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        for user in users
    ]

# TODO: Admin Only
@app.get("/accounts")
def get_accounts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    accounts = (
        db.query(Account)
        .filter(Account.user_id == int(current_user["sub"]))
        .all()
    )

    return [
        {
            "acc_id": a.acc_id,
            "user_id": a.user_id,
            "acc_type": a.acc_type,
            "balance": a.balance
        }
        for a in accounts
    ]
# TODO: Admin Only
# TODO: Admin Only
@app.get("/all-transactions")
def all_transactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("sub") != "1":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    transactions = db.query(Transaction).all()

    return [
        {
            "id": t.id,
            "acc_id": t.acc_id,
            "transaction_type": t.transaction_type,
            "amount": t.amount,
            "created_at": t.created_at
        }
        for t in transactions
]

@app.get("/statement/{acc_id}")
def account_statement(
    acc_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.acc_id == acc_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    if str(account.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: You can only view statements for your own accounts."
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.acc_id == acc_id)
        .order_by(Transaction.id.desc())
        .all()
    )
    return {
        "account_id": account.acc_id,
        "balance": account.balance,
        "transactions": [
    {
        "id": t.id,
        "transaction_type": t.transaction_type,
        "amount": t.amount
    }
    for t in transactions
]
    }
# TODO: Restrict this endpoint to admin users
# TODO: Restrict this endpoint to admin users
@app.put("/loan/{loan_id}/approve")
def approve_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("sub") != "1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
        
    loan = db.query(Loan).filter(Loan.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    loan.status = "Approved"
    db.commit()
    db.refresh(loan)
    return {"message": "Loan Approved successfully", "status": loan.status}
@app.get("/loan/{loan_id}")
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    loan = db.query(Loan).filter(
        Loan.loan_id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if str(loan.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    return {
    "loan_id": loan.loan_id,
    "user_id": loan.user_id,
    "amount": loan.amount,
    "status": loan.status
}

@app.delete("/account/{acc_id}")
def delete_account(
    acc_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.acc_id == acc_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    if str(account.user_id) != current_user.get("sub"):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: You cannot delete an account belonging to another user."
        )
    
    # --- CRITICAL FIX: Delete associated transactions first to prevent Foreign Key crashes ---
    transactions = db.query(Transaction).filter(Transaction.acc_id == acc_id).all()
    for transaction in transactions:
        db.delete(transaction)
    
    # Now it's completely safe to delete the main account record
    db.delete(account)
    db.commit()
    
    return {"message": "Account and all associated transaction histories deleted successfully"} 
@app.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .all()
    )

    total_balance = sum(a.balance for a in accounts)

    transaction_count = (
    db.query(Transaction)
    .join(Account, Account.acc_id == Transaction.acc_id)
    .filter(Account.user_id == user_id)
    .count()
)

    return {
        "user_id": user_id,
        "total_accounts": len(accounts),
        "total_balance": total_balance,
        "total_transactions": transaction_count
}