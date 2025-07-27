import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models import Message

def export_messages_to_csv(db: Session):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "content", "timestamp", "user_id", "room_id"])
    
    messages = db.query(Message).all()
    for msg in messages:
        writer.writerow([msg.id, msg.content, msg.timestamp, msg.user_id, msg.room_id])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=messages.csv"}
    )
