# run.py or manage.py

from app import create_app
from app.controllers.usersController import usersController

app = create_app()  # Initialize the app

# Register blueprints and other configurations
app.register_blueprint(usersController)

if __name__ == "__main__":
    app.run(debug=True)
