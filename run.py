# run.py or manage.py

from app import create_app
from app.controllers.usersController import usersController
from flask_cors import CORS

app = create_app()  # Initialize the app

CORS(app, origins="http://localhost:3000")

# Register blueprints and other configurations
app.register_blueprint(usersController)

if __name__ == "__main__":
    app.run(debug=True)
