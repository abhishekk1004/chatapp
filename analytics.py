from fastapi import APIRouter
from sqlalchemy import func
from models import Room, Message, User
from database import SessionLocal
from typing import Optional
from datetime import datetime

analytics_router = APIRouter()

@analytics_router.get("/analytics/messages-per-room")
def messages_per_room():
    db = SessionLocal()
    result = db.query(Room.name, func.count(Message.id))\
               .join(Message, Room.id == Message.room_id)\
               .group_by(Room.name).all()
    return dict(result)

@analytics_router.get("/analytics/user-activity")
def user_activity():
    db = SessionLocal()
    result = db.query(User.username, func.count(Message.id))\
               .join(Message, User.id == Message.sender_id)\
               .group_by(User.username).all()
    return dict(result)

@analytics_router.get("/analytics/messages-date-filter")
def messages_with_date(start: Optional[str] = None, end: Optional[str] = None):
    db = SessionLocal()
    query = db.query(Message)

    if start:
        query = query.filter(Message.timestamp >= datetime.fromisoformat(start))
    if end:
        query = query.filter(Message.timestamp <= datetime.fromisoformat(end))

    return [{"content": m.content, "timestamp": m.timestamp.isoformat()} for m in query.all()]
