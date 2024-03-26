from flask_socketio import SocketIO 
from .database import Database

io = SocketIO()

db = Database()