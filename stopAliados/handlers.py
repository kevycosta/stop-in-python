from .server import db
from .extensions import io

class RoundManager:
    def __init__(self):
        self.count = 0
        self.round_on = False
        self.round_max_time = 90

    def run_background_count(self):
        while self.round_on:
            self.count += 1
            print(self.count)
            time.sleep(1)
            io.emit('progress_update', {'progress': 1 + self.count})

            if self.count == self.round_max_time:
                self.round_on = False
                self.count = 0

    def start_round(self):
        print("Starting Round!!")
        self.round_on = True
        self.run_background_count()

    def finish_round(self):
        print("Finishing Round!!")
        self.round_on = False
        self.count = 0


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


# def cancel_register_user_login(event:dict):
#     print("userLogin Event: ", event);

#     room_id = int(event.get("room_id"))
    
#     dataRoomUsersList = get_all_users_in_a_room(room_id)
#     all_users_list = [x.get("user_id") for x in dataRoomUsersList]

#     if event.get("user_id") not in all_users_list:
#         tp_data = {
#             "room_id" : room_id,
#             "user_id" : event.get("user_id"),
#             "user_score" : 0
#         }
        
#         db.dcRoomStatus.create(tp_data)
#         print(f"User {event.get('user_id')} registered on Room {room_id}.")


def get_all_users_in_a_room(room_id: int):
    dataRoomUsers = db.dcRoomStatus.query_raw(
        f"""
            select drs.room_id,
            drs.user_id,
            drs.user_score,
            mu.user_name
            from dcRoomStatus as drs
            inner join mdUsers as mu
                on drs.user_id = mu.user_id
            where drs.room_id = {room_id}
        """
    )

    dataRoomUsersList = [x.model_dump() for x in dataRoomUsers]

    return dataRoomUsersList

