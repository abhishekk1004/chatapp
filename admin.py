# admin.py
from sqladmin import Admin, ModelView
from fastapi import FastAPI, APIRouter, Depends
from models import User, Room, Message
from database import engine, SessionLocal

from database import get_db
from utils.export import export_messages_to_csv
from dependencies import get_current_admin_user 

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.role]

class RoomAdmin(ModelView, model=Room):
    column_list = [Room.id, Room.name]

class MessageAdmin(ModelView, model=Message):
    column_list = [Message.id, Message.content, Message.timestamp]

def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(RoomAdmin)
    admin.add_view(MessageAdmin)



router = APIRouter()

@router.get("/export/messages", dependencies=[Depends(get_current_admin_user)])
def export_csv(db=Depends(get_db)):
    return export_messages_to_csv(db)
