from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # admin or user
    messages = relationship("Message", back_populates="sender")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    messages = relationship("Message", back_populates="room")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    sender = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")
