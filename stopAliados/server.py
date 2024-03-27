
from flask import Blueprint, session, url_for, redirect, request, flash, jsonify
from flask.templating import render_template

from .extensions import io, db
from .helpers import login_required
from .handlers import get_all_open_rooms

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def home():
    user_name = session.get("user_name", None)

    rooms_list = get_all_open_rooms()

    return render_template(
        "home.html", 
        user_name=user_name, 
        rooms_list=rooms_list
    )


@main.route("/login", methods=["GET", "POST"])
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


@main.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@main.route("/create_room", methods=["GET", "POST"])
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


@main.route("/play/<room_id>", methods=["GET"])
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
