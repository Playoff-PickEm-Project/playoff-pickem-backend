from flask import Flask

def create_app():
    app = Flask(__name__)

    from .home_screen import home_screen as home_screen_blueprint
    app.register_blueprint(home_screen_blueprint)

    return app