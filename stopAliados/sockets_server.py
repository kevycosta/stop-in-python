from .server import session
from .extensions import io, db
from .handlers import (
    RoundManager,
    register_user_login, 
    cancel_register_user_login,
    get_all_users_in_a_room,
    register_round_answers,
    register_votes_results
)

# Initialize the RoundManager
round_manager = RoundManager()

#### IO Sockets ####
@io.on('connect')
def handle_connect():
    print('Client connected')

    register_user_login({
        "user_id":session.get("user_id"), 
        "room_id":session.get("room_id")
    })

    round_manager.room_id = int(session.get("room_id")) 
    round_manager.current_round = db.dcRoomRound.find_first(
            where={"room_id":int(session.get("room_id"))}
        ).current_round 

    data_dict = {
        "users_data" : get_all_users_in_a_room(int(session.get("room_id"))),
        "user_id" : session.get("user_id"),
        "room_id" : round_manager.room_id,
        "current_round" : round_manager.current_round,
        "random_letter" : round_manager.letter_in_round,
        "under_evaluation" : round_manager.under_evaluation,
        "current_theme" : round_manager.current_theme
    }

    io.emit("inUserConnect", data_dict)


@io.on("disconnect")
def handle_disconnect():
    print('Client disconnected')

    # cancel_register_user_login({
    #     "user_id":session.get("user_id"), 
    #     "room_id":session.get("room_id")
    # })

    io.emit("newUserLogged", get_all_users_in_a_room(int(session.get("room_id"))))


@io.on('startRound')
def start_round():
    round_manager.start_round()


@io.on('finishRound')
def finish_round():
    io.emit("roundServerFinish")


@io.on('roundServerFinish')
def server_finish_round_for_all_users(data):
    print(data)

    room_id = int(session.get("room_id"))
    user_id = session.get("user_id")

    register_round_answers(
        room_id=room_id,
        user_id=user_id,
        letter_in_round=round_manager.letter_in_round,
        current_round=round_manager.current_round,
        data=data
    )

    round_manager.finish_round()
    round_manager.evaluatingVotes()


@io.on("finishEvaluation")
def finish_evaluation():
    io.emit("serverFinishEvaluation")
    round_manager.evaluatingVotes()


@io.on("serverFinishEvaluation")
def server_finish_evaluation_votes(data):
    room_id = int(session.get("room_id"))
    user_id = session.get("user_id")

    print(f"Results of {user_id} in room_id: {room_id}", data);

    register_votes_results(
        room_id=room_id, 
        user_id=user_id, 
        data=data
    )

