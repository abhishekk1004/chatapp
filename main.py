from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserCreate, Token
from auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from websocket import router as websocket_router
from models import Room
from fastapi import Body
from admin import setup_admin

from analytics import analytics_router



app = FastAPI()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = User(username=user.username, password=hash_password(user.password), role=user.role)
    db.add(new_user)
    db.commit()
    return {"msg": "User created"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/rooms")
def create_room(name: str = Body(...), db: Session = Depends(get_db)):
    room = Room(name=name)
    db.add(room)
    db.commit()
    return {"msg": f"Room '{name}' created."}


app.include_router(websocket_router)
setup_admin(app)


app.include_router(analytics_router)