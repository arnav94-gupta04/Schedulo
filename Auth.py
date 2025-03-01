from database import ScheduloDatabase

# Initialize the database instance (it will create the Users table if needed)
db = ScheduloDatabase()

def sign_up(first_name, last_name, email, password):
    success = db.insert_user(first_name, last_name, email, password)
    return success

def login(email, password):
    user = db.get_user(email, password)
    return user

# Simple command-line interface for testing
if __name__ == "__main__":
    print("Welcome to Schedulo Authentication")
    mode = input("Do you want to (l)ogin or (s)ignup? ")
    if mode.lower() == "s":
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        email = input("Email: ")
        password = input("Password: ")
        if sign_up(first_name, last_name, email, password):
            print("Signup successful! Please log in.")
        else:
            print("Signup failed: Email already exists.")
    elif mode.lower() == "l":
        email = input("Email: ")
        password = input("Password: ")
        user = login(email, password)
        if user:
            print(f"Welcome, {user['first_name']} {user['last_name']}!")
        else:
            print("Invalid email or password.")
