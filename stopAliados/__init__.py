from flask import Flask 
from flask_cors import CORS

from .sockets_server import io
from .server import main 

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret"
    app.secret_key = '#@34Ask&5$aJ'
    CORS(app)

    app.register_blueprint(main)
    io.init_app(app)

    return app