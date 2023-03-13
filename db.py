import json
from re import match
import sqlite3
import hashlib


class AuthenticationError(Exception):
    """Raised when trying to log in with incorrect details"""


class UserAlreadyExists(Exception):
    """Raised when trying to create a user that is already in the database"""


class UserDatabase:

    def __init__(self, filename: str):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS Users (
            username VARCHAR(50) PRIMARY KEY,
            passwd_hash BLOB(32) NOT NULL,
            email_address VARCHAR(50) UNIQUE
            );""")

    def login(self, username: str, passwd_hash: bin):
        self.c.execute(f"""SELECT passwd_hash FROM Users WHERE username="{username}";""")
        r = self.c.fetchone()
        if r is None:
            raise AuthenticationError("Username not found in database")
        if r[0] != str(passwd_hash)[2:]:
            raise AuthenticationError("Password is incorrect")
        return True

    def add_user(self, username: str, passwd_hash: bin, email_address: str = ""):
        pw = str(passwd_hash)[2:]
        try:
            if email_address == "":
                self.c.execute(f"""INSERT INTO Users (username, passwd_hash)
                VALUES ("{username}", "{pw}");""")
            else:
                if check_email(email_address):
                    self.c.execute(f"""INSERT INTO Users (username, passwd_hash, email_address)
                    VALUES ("{username}", "{pw}", "{email_address}");""")
                else:
                    raise ValueError("Invalid Email Address")
        except sqlite3.IntegrityError:
            raise UserAlreadyExists()

    def get_user_data(self, username: str):
        fields = ["username", "email_address"]
        self.c.execute(f"""SELECT {", ".join(fields)} FROM Users WHERE username="{username}";""")
        data = self.c.fetchone()
        return json.dumps(dict(zip(fields, data)))

    def remove_user(self, username: str, passwd_hash: bin):
        if self.login(username, passwd_hash):
            self.c.execute(f"""DELETE FROM Users WHERE username="{username}";""")

    def change_email(self, username: str, password_hash: bin, email_address: str):
        if check_email(email_address):
            if self.login(username, password_hash):
                self.c.execute(f"""UPDATE Users SET email_address = "{email_address}"
                WHERE username = "{username}";""")
            else:
                raise AuthenticationError("Login failed but didn't raise an error")
        else:
            raise ValueError("Invalid Email Address")

    def change_password(self, username: str, current_password_hash: bin, new_password_hash: bin):
        if self.login(username, current_password_hash):
            self.c.execute(f"""UPDATE Users SET passwd_hash = "{str(new_password_hash)[2:]}"
            WHERE username = "{username}";""")
        else:
            raise AuthenticationError("Login failed but didn't raise an error")

    def __repr__(self):
        self.c.execute("SELECT * FROM Users")
        a = self.c.fetchall()
        return "\n".join(", ".join(b) for b in a)

    def __del__(self):
        self.conn.commit()
        self.conn.close()


def hash_password(passwd: str) -> bin:
    return bin(int(hashlib.sha256(passwd.encode('utf-8')).hexdigest(), 16))


def check_email(email_address: str) -> bool:
    return bool(match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.["
                      r"a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email_address))


if __name__ == "__main__":
    db = UserDatabase("test_database.db")
    inp = ""
    while inp not in ("q", "quit"):
        print("[S]how all entries in the database")
        print("[A]dd a user to the database")
        print("[L]ogin")
        print("[R]emove a user from the database")
        print("[Q]uit")
        inp = input("> ").lower()
        if inp == "s":
            print(repr(db))
        elif inp == "a":
            db.add_user(input("Username: "), hash_password(input("Password: ")), input("Email: "))
        elif inp == "l":
            try:
                if db.login(input("Username: "), hash_password(input("Password: "))):
                    print("Login successful")
                else:
                    print("Login failed")
            except AuthenticationError as e:
                print(f"Login failed: {e}")
        elif inp == "r":
            try:
                db.remove_user(input("Username: "), hash_password(input("Password: ")))
            except AuthenticationError as e:
                print(f"Error: {e}")
            finally:
                print("User successfully removed")
