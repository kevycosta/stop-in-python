import time

from flask import Flask, session, url_for, redirect, request, flash, jsonify
from flask.templating import render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from database import Database
from helpers import login_required

db = Database()

app = Flask(__name__)
app.secret_key = '#@34Ask&5$aJ'

CORS(app)

io = SocketIO(app)

_users_connected = {}
_round_on = False
_round_start_time = 0
_round_max_time = 90

@app.route("/")
@login_required
def home():
    user_name = session.get("user_name", None)
    return render_template("home.html", user_name=user_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        user_login = request.form.get("username")
        user_password = request.form.get("password")

        # Ensure username was submitted
        if not user_login:
            flash("Por favor insira um username.")
            return render_template("login.html")

        # Ensure password was submitted
        elif not user_password:
            flash("Por favor insira uma senha.")
            return render_template("login.html")

        # Query database for username
        userData = db.mdUsers.find_first(where={"user_login" : user_login})

        # Ensure username exists and password is correct
        if userData != None:
            userData = userData.model_dump()
        else:
            flash("Esse username não existe!")
            return render_template("login.html")

        if user_password != userData.get("user_password"):
            flash("Senha errada painho!")
            return render_template("login.html")
        else:
            # Remember which user has logged in
            session["user_id"] = userData.get("user_id")
            session["user_name"] = userData.get("user_name")

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/create_room", methods=["GET", "POST"])
@login_required
def manage_room():
    if request.method == "GET":
        return render_template("create_room.html")
    else:

        json_object = request.json
        print(json_object);

        if json_object == None:
            return render_template("create_room.html")

        room_id = db.mdRooms.create(data={"user_admin" : session.get("user_id")}).room_id
        print(f"\n Created room_id: {room_id} \n")

        db.dcRoomRound.create({"room_id" : room_id})
        
        questions_inputed = []
        for theme in json_object.get("themes_list"):
            question_obj = {
                "room_id" : room_id,
                "question_title" : theme,
            }

            result = db.mdQuestions.create(data=question_obj).model_dump()
            questions_inputed.append(result);

        print(f"\n Created themes from room_id: {room_id} themes_data: {questions_inputed}\n")

        return jsonify({'success': True, 'room_id': room_id})


@app.route("/play/<room_id>", methods=["GET", "POST"])
@login_required
def play_room(room_id):
    if request.method == "GET":
        session['room_id'] = room_id

        questions_data = db.mdQuestions.find_many(where={"room_id" : int(room_id)})
        questions_array = [x.model_dump() for x in questions_data]

        user_adm = db.mdRooms.find_first(where={"room_id" : int(room_id)}).user_admin
        print("user_adm", user_adm)

        current_round = db.dcRoomRound.find_first(where={"room_id" : int(room_id)}).current_round

        is_admin = session.get("user_id") == user_adm

        return render_template(
            "play.html", 
            room_id=room_id,
            themes_data=questions_array,
            is_admin=is_admin,
            current_round=current_round
        )
    else:
        return render_template("play.html", room_id=room_id)



#### IO Sockets ####
@io.on('connect')
def handle_connect():
    print('Client connected')

    register_user_login({
        "user_id":session.get("user_id"), 
        "room_id":session.get("room_id")
    })


def register_user_login(event:dict):
    print("userLogin Event: ", event);

    if event.get("room_id") not in _users_connected:
        _users_connected[event["room_id"]] = []
    elif event.get("room_id") in _users_connected:
        pass
    else:
        _users_connected[event["room_id"]].append(event.get("user_id"))

    if len(_users_connected) > 0:
        dataRoomUsers = db.dcRoomStatus.find_many(where={"room_id" : int(session.get("room_id"))})
        dataRoomUsersList = [x.model_dump() for x in dataRoomUsers]

        if len(dataRoomUsersList) > 0:
            for u in _users_connected[session.get("room_id")]:
                if u['user_id'] not in _users_connected[session.get("room_id")]:
                    tp_data = {
                        "room_id" : session.get("room_id"),
                        "user_id" : u['user_id'],
                        "user_score" : 0
                    }
                    
                    db.dcRoomStatus.create(tp_data)

    io.emit("allUsersLogged", _users_connected)

def run_background_count():
    count = _round_start_time
    _round_on = _round_on
    
    while _round_on:
        count += 1
        time.sleep(1)
        io.emit('progress_update', {'progress': 1+count})

        if count == _round_max_time:
            _round_on = False

@io.on('startRound')
def start_round():
    _round_on = True  
    io.start_background_task(run_background_count)


@io.on('finishRound')
def finish_round():
    _round_on = False

if __name__ == "__main__":
    io.run(app, debug=True)