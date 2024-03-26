from prisma import Prisma, register
from prisma.models import (
    mdUsers, mdRooms, dcRoomStatus, dcRoomRound,
    mdQuestions, dcQuestionsTransactions
)

db = Prisma()
if not db.is_connected():
    register(db)
    db.connect()

class Database():
    def __init__(self) -> None:
        self.db = db
        self.is_connected = True

        self.mdUsers = mdUsers.prisma()
        self.mdRooms = mdRooms.prisma()
        self.dcRoomRound = dcRoomRound.prisma()
        self.dcRoomStatus = dcRoomStatus.prisma()
        self.mdQuestions = mdQuestions.prisma()
        self.dcQuestionsTransactions = dcQuestionsTransactions.prisma()

    def connect(self):
        if not self.is_connected():
            self.db.connect()
            self.is_connected = True

    def disconn(self):
        if self.is_connected():
            self.db.disconnect()
            self.is_connected = False
    
    def __del__(self):
        self.db.disconnect()

    def query_db(self, query:str):
        return self.db.query_raw(query=query)
    
    def __str__(self) -> str:
        return f"Prisma Database Stop Game class {self.db}"
