from fastapi import FastAPI, Depends, HTTPException, Body, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User, Room
from schemas import UserCreate, Token
from auth import hash_password, verify_password, create_access_token
from websocket import router as websocket_router
from admin import setup_admin
from analytics import analytics_router

# Initialize FastAPI app
app = FastAPI()

# Templates and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User signup route
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = User(username=user.username, password=hash_password(user.password), role=user.role)
    db.add(new_user)
    db.commit()
    return {"msg": "User created"}

# Login route returning JWT token
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# Room creation
@app.post("/rooms")
def create_room(name: str = Body(...), db: Session = Depends(get_db)):
    room = Room(name=name)
    db.add(room)
    db.commit()
    return {"msg": f"Room '{name}' created."}

# Web UI: Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Web UI: Login page
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Web UI: Login POST handler (redirect-based, for form login)
@app.post("/token")
def login_post(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)

# Web UI: Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Include WebSocket and analytics routers
app.include_router(websocket_router)
app.include_router(analytics_router)

# Setup admin routes
setup_admin(app)
