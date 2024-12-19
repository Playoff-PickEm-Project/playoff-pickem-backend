from app.models.userModel import Users

# Method to get all users - probably won't use but worth having
def get_all_users():
    return Users.query.all()

# Method to get a user by id - note the format of the return statement (querying by id doesn't require a filter_by thing)
def get_user_by_id(user_id):
    return Users.query.get(user_id)

# Method to get a user by username - note the format of the return statement
def get_user_by_username(username):
    return Users.query.filter_by(username=username).first()