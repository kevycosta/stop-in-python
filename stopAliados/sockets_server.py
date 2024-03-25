from .server import session
from .extensions import io
from .handlers import register_user_login, RoundManager

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

@io.on("disconnect")
def handle_disconnect():
    print('Client disconnected')

    # cancel_register_user_login({
    #     "user_id":session.get("user_id"), 
    #     "room_id":session.get("room_id")
    # })

@io.on('startRound')
def start_round():
    round_manager.start_round()

@io.on('finishRound')
def finish_round():
    round_manager.finish_round()


