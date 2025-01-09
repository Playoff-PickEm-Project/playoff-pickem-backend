# run.py file to run the flask application. Run with 'python3 run.py'

from app import create_app
from app.controllers.propController import propController
from app.controllers.usersController import usersController
from app.controllers.leagueController import leagueController
from app.controllers.gameController import gameController
from flask_cors import CORS

app = create_app()  # Initialize the app

CORS(app, origins="http://localhost:3000")

# Register blueprints and other configurations
app.register_blueprint(usersController)
app.register_blueprint(leagueController)
app.register_blueprint(gameController)
app.register_blueprint(propController)

if __name__ == "__main__":
    app.run(debug=True)
