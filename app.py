from flask import Flask, render_template, request, redirect, session
from db import UserDatabase, hash_password, UserAlreadyExists, AuthenticationError
import os

app = Flask(__name__)
app.secret_key = "the secret key"

@app.route("/gui/remove_user")
def delete_user_gui():
    try:
        return render_template("remove_user.html", username=session["username"])
    except KeyError:
        return "Not logged in", 401

@app.route("/log_in", methods=["POST"])
def log_in():
    username = request.values.get("username")
    password_hash = hash_password(request.values.get("password"))
    try:
        if db.login(username, password_hash):
            session["username"] = username
            session["loggedIn"] = True
            if url:=request.values.get("redirect") is None: return redirect(url)
            return "Logged in", 200
    except AuthenticationError as e:
        return str(e), 401
    except ValueError as e:
        return str(e), 400


@app.route("/delete_user")
def delete_user():
    if session.get("loggedIn", False):
        try:
            username=session["username"]
            db.remove_user(username)
            session.clear()
            if url:=request.values.get("redirect") is None: return redirect(url)
            return f"User {username} successfully removed", 200
        except ValueError as e:
            return str(e), 401
    else:
        return "Not logged in", 401


@app.route("/gui/login")
def login_gui():
    return render_template("login.html")


@app.route("/gui/add_user")
def add_user_gui():
    return render_template("add_user.html")


@app.route("/gui/change_password")
def change_password_gui():
    if session.get("loggedIn", False):
        return render_template("change_password.html")
    return "Not logged in", 401


@app.route("/")
def homepage():
    return render_template("index.html", loggedIn=session.get("loggedIn", False)), 200


@app.route("/add_user", methods=["POST"])
def add_user():
    email = request.values.get("email")
    username = request.values.get("username")
    if username is None: raise ValueError("username not given")
    password = request.values.get("password")
    if password is None: raise ValueError("password not given")
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
    if url:=request.values.get("redirect") is None: return redirect(url)
    return "Added", 201


@app.route("/logout")
def logout():
    session.clear()
    if url:=request.values.get("redirect") is None: return redirect(url)
    return "Successfully logged out", 200


@app.route("/get_data")
def get_data():
    return db.get_user_data(session["username"]), 200
    username = request.values.get("username")
    try:
        return db.get_user_data(username), 200
    except AuthenticationError as e:
        return str(e), 401
    except ValueError as e:
        return str(e), 401


@app.route("/change_password", methods=["POST"])
def change_password():
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
    if url:=request.values.get("redirect") is None: return redirect(url)
    return "Password changed successfully", 200


@app.route("/change_email", methods=["POST"])
def change_email():
    username = request.values.get("username")
    email = request.values.get("email")
    if session.get("loggedIn", False):
        try:
            db.change_email(username, email)
        except AuthenticationError as e:
            return str(e), 401
        except ValueError as e:
            return str(e), 401
        finally:
            if url:=request.values.get("redirect") is None: return redirect(url)
            return f"Email for {username} successfully changed to {email}", 200


@app.route("/debug")
def show_db():
    global db
    return repr(db)


db = UserDatabase("test_database.db")
if __name__ == '__main__':
    os.remove("test_database.db")
    app.run(debug=True)
