from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from auth import decode_token
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Message, User, Room
from typing import Dict

router = APIRouter()

# Keep track of connected clients in rooms
connected_clients: Dict[int, list] = {}  # {room_id: [websocket1, websocket2, ...]}

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str):
    payload = decode_token(token)
    if payload is None:
        await websocket.close()
        return

    username = payload.get("sub")

    await websocket.accept()

    if room_id not in connected_clients:
        connected_clients[room_id] = []
    connected_clients[room_id].append(websocket)

    db: Session = SessionLocal()

    # 📨 Send last 10 messages
    recent_messages = db.query(Message).filter(Message.room_id == room_id).order_by(Message.timestamp.desc()).limit(10).all()
    for msg in reversed(recent_messages):
        await websocket.send_text(f"{msg.sender.username}: {msg.content}")

    try:
        while True:
            data = await websocket.receive_text()

            # Save message
            user = db.query(User).filter(User.username == username).first()
            message = Message(content=data, sender_id=user.id, room_id=room_id)
            db.add(message)
            db.commit()

            # Broadcast message
            for client in connected_clients[room_id]:
                await client.send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        connected_clients[room_id].remove(websocket)
