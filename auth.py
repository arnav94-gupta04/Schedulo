import bcrypt
from database import ScheduloDatabase

class AuthService:
    def __init__(self, db=None):
        self.db = db or ScheduloDatabase()

    def sign_up(self, first_name, last_name, email, password):
        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return self.db.insert_user(first_name, last_name, email, hashed_password)

    def login(self, email, password):
        user = self.db.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None

if __name__ == "__main__":
    auth_service = AuthService()
    print("Welcome to Schedulo Authentication")
    mode = input("Do you want to (l)ogin or (s)ignup? ")
    if mode.lower() == "s":
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        email = input("Email: ")
        password = input("Password: ")
        if auth_service.sign_up(first_name, last_name, email, password):
            print("Signup successful! Please log in.")
        else:
            print("Signup failed: Email may already exist.")
    elif mode.lower() == "l":
        email = input("Email: ")
        password = input("Password: ")
        user = auth_service.login(email, password)
        if user:
            print(f"Welcome, {user['first_name']} {user['last_name']}!")
        else:
            print("Invalid email or password.")
