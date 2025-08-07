from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import engine, SessionLocal
from models import Base, User
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)
app = FastAPI()

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()
        
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/register")
def register_user(user: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    new_user = User(
        username=user.username,
        email = user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/login")
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"message":"Login succesful"}