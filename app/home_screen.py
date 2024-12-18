from flask import Blueprint

home_screen = Blueprint('home-screen', __name__)

@home_screen.route('/')
def index():
    return "hello world"