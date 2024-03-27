import time
import random
import string

from .server import db
from .extensions import io

class RoundManager:
    def __init__(self):
        self.count = 0
        self.room_id = 0
        self.round_on = False
        self.letter_in_round = ""
        self.current_round = 1
        self.round_max_time = 90
        self.under_evaluation = False
        self.question_theme_to_evaluate = ""
        self.themes_data = get_all_themes_by_round(self.room_id)

    def run_background_count(self):
        while self.round_on:
            self.count += 1
            time.sleep(1)
            io.emit('progress_update', {'progress': 1 + self.count})

            if self.count == self.round_max_time:
                self.round_on = False
                self.count = 0
                self.finish_round()

    def random_letter(self):
        self.letter_in_round = random.choice(string.ascii_uppercase)

    def next_round(self):
        self.random_letter()
        self.start_round()

    def start_round(self):
        if self.current_round > 12:
            print("Game ended.")
            io.emit("finishGame")
        else:
            print(f"Starting Round {self.current_round}!")
            self.round_on = True
            self.random_letter()

            round_info_dict = {
                "random_letter" : self.letter_in_round,
                "current_round" : self.current_round
            }

            io.emit("roundInfo", round_info_dict)
            self.run_background_count()

    def finish_round(self):
        print(f"Finishing Round ! {self.current_round}")
        self.round_on = False
        self.count = 0 

        self.start_evaluation()
    
    def start_evaluation(self):
        print("Starting evaluation of questions !!!")
        self.under_evaluation = True

        answers_data = get_all_answers_by_round(self.room_id, self.current_round)

        evaluation_dict = {
            "evaluation_status" : self.under_evaluation,
            "answers_data" : answers_data
        }

        io.emit("evaluating", evaluation_dict) # Start evaluating on frontend
    
    def finish_evaluation(self):
        print("Finishing evaluation of questions !!!")
        self.under_evaluation = False
        self.current_round = db.dcRoomRound.update(
            data={"current_round" : self.current_round + 1},
            where={"room_id":self.room_id}
        ).current_round

        evaluation_dict = {
            "evaluation_status" : self.under_evaluation,
        }

        io.emit("evaluating", evaluation_dict)
        
        self.next_round()
    
    def evaluatingVotes(self):
        next_theme = self.get_next_theme()
        if next_theme:
            io.emit('roundTheme', next_theme)
        else:
            self.finish_evaluation()

    def get_next_theme(self):
        if self.themes_data:
            return self.themes_data.pop(0)
        return None
        
        

def register_round_answers(
        room_id: int,
        user_id: str,
        letter_in_round: str,
        current_round: int,
        data: dict
    ):

    for item in data:
        insert_dict = {
            "question_id" : int(item.get("question_id")),
            "user_id" : user_id,
            "room_id" : room_id,
            "round" : current_round,
            "letter_in_round" : letter_in_round,
            "question_value" : item.get("question_value", ""),
            "question_votes" : 0
        }

        db.dcQuestionsTransactions.create(insert_dict)


def register_user_login(event:dict):
    print("userLogin Event: ", event);

    room_id = int(event.get("room_id"))
    
    dataRoomUsersList = get_all_users_in_a_room(room_id)
    all_users_list = [x.get("user_id") for x in dataRoomUsersList]

    if event.get("user_id") not in all_users_list:
        tp_data = {
            "room_id" : room_id,
            "user_id" : event.get("user_id"),
            "user_score" : 0
        }
        
        db.dcRoomStatus.create(tp_data)
        print(f"User {event.get('user_id')} registered on Room {room_id}.")


def cancel_register_user_login(event:dict):
    print("userLogin Event: ", event);

    room_id = int(event.get("room_id"))
    
    db.dcRoomStatus.delete(where={"user_id":event.get("user_id")})

    print(f"User {event.get('user_id')} removed of Room {room_id}.")


def get_all_users_in_a_room(room_id: int):
    dataRoomUsers = db.query_db(
        f"""
            select drs.room_id,
            drs.user_id,
            mu.user_name,
            drs.user_score
            from dcRoomStatus as drs
            join mdUsers as mu
                on drs.user_id = mu.user_id
            where drs.room_id = {room_id}
        """
    )

    dataRoomUsersList = [x for x in dataRoomUsers]

    return dataRoomUsersList


def get_all_open_rooms():
    dataRoomRound = db.dcRoomRound.find_many(where={"current_round" : 0})
    dataRoomsList = [x.model_dump() for x in dataRoomRound]

    return dataRoomsList
    

def get_all_answers_by_round(room_id:int, round:int):
    query = f"""
        select 
        dqt.question_id,
        mq.question_title,
        dqt.user_id,
        mu.user_name,
        dqt.room_id,
        dqt.round,
        dqt.letter_in_round,
        dqt.question_value,
        dqt.question_votes
        from dcQuestionsTransactions as dqt
        inner join mdUsers mu
            on dqt.user_id = mu.user_id
        inner join mdQuestions mq
            on dqt.question_id = mq.question_id
        where dqt.room_id = {int(room_id)}
        and dqt.round = {int(round)}
    """

    answers_data = db.query_db(query)

    return answers_data


def get_all_themes_by_round(room_id:int):
    query = f"""
        select distinct
        mq.question_id,
        mq.question_title
        from mdQuestions mq
        where mq.room_id = {int(room_id)}
    """

    themes_data = db.query_db(query)

    return themes_data

