from flask import Flask, render_template, request
from db import UserDatabase, hash_password, UserAlreadyExists, AuthenticationError
import os

app = Flask(__name__)


@app.route("/delete_user", methods=["POST"])
def delete_user():
    username = request.values.get("username")
    password = request.values.get("password")
    password_hash = hash_password(password)
    try:
        db.remove_user(username, password_hash)
    except AuthenticationError as e:
        return str(e), 401
    except ValueError as e:
        return str(e), 401
    finally:
        return f"User {username} successfully removed", 200


@app.route("/gui/add_user")
def add_user_gui():  # put application's code here
    return render_template("add_user.html")


@app.route("/gui/change_password")
def change_password_gui():
    return render_template("change_password.html")


@app.route("/add_user", methods=["POST"])
def add_user():
    print(repr(db))
    email = request.values.get("email")
    username = request.values.get("username")
    password = request.values.get("password")
    password_hash = hash_password(password)
    if len(username) > 50:
        return "username too long", 400
    try:
        if email is None:
            db.add_user(username, password_hash)
        else:
            if len(email) > 50:
                return "email too long", 400
            db.add_user(username, password_hash, email)
    except UserAlreadyExists:
        return "There is already a user with that username in the database", 400
    except ValueError as e:
        print(email)
        return str(e), 401
    return "Added", 201


@app.route("/get_data")
def get_data():
    username = request.values.get("username")
    try:
        return db.get_user_data(username), 200
    except AuthenticationError as e:
        return str(e), 401
    except ValueError as e:
        return str(e), 401


@app.route("/change_password", methods=["POST"])
def change_password():
    print(repr(db))
    username = request.values.get("username")
    old_password = request.values.get("old_password")
    old_hash = hash_password(old_password)
    new_password = request.values.get("new_password")
    new_hash = hash_password(new_password)
    try:
        db.change_password(username, old_hash, new_hash)
    except AuthenticationError as e:
        return str(e), 401
    except ValueError as e:
        return str(e), 401
    return "Password changed successfully", 200


@app.route("/change_email", methods=["POST"])
def change_email():
    username = request.values.get("username")
    password = request.values.get("password")
    password_hash = hash_password(password)
    email = request.values.get("email")
    try:
        db.change_email(username, password_hash, email)
    except AuthenticationError as e:
        return str(e), 401
    except ValueError as e:
        return str(e), 401
    finally:
        return f"Email for {username} successfully changed to {email}", 200


@app.route("/debug")
def show_db():
    global db
    return repr(db)


db = UserDatabase("test_database.db")
if __name__ == '__main__':
    os.remove("test_database.db")
    app.run(debug=True)
