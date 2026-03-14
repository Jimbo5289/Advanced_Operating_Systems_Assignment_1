from datetime import datetime  # Used to create readable timestamps for log entries
import os                      # Will be used later for file checks and submission handling
import hashlib                 # Will be used later for duplicate file detection with hashing
import time                    # Used to track login timing and suspicious repeated attempts

# File used to record submissions, login events, and security-related activity
LOG_FILE = "submission_log.txt"
SUBMISSION_RECORD_FILE = "submitted_files.txt"   # File used to store previous submission records
MAX_FILE_SIZE = 5 * 1024 * 1024                  # Maximum allowed file size: 5 MB in bytes
ALLOWED_EXTENSIONS = [".pdf", ".docx"]          # Only these file types are accepted

# Dictionary of valid users for this coursework prototype.
# In a real system, passwords would be securely hashed and stored in a database.
USERS = {
    "student1": "password123",
    "student2": "securepass456"
}

# Track the currently logged-in user.
# If no user is logged in, the value remains None.
logged_in_user = None

# Track failed login attempts per user.
# This supports the account lock requirement after repeated failures.
failed_attempts = {}

# Track recent login attempt times per user.
# This is used to detect repeated attempts within 60 seconds.
login_attempt_history = {}


def log_event(message):
    # Create a timestamp in a clear year-month-day hour:minute:second format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode so previous records are preserved
    with open(LOG_FILE, "a") as log:
        # Write the timestamp and the supplied message to the log file
        log.write(f"{timestamp} : {message}\n")


def show_menu():
    # Display the main menu for the secure submission system
    print("\n========== SECURE EXAM SUBMISSION SYSTEM ==========")
    print("1. Login")
    print("2. Submit Exam File")
    print("3. View Submission Log")
    print("4. Exit")
    print("=" * 50)


def login():
    global logged_in_user  # Allows the function to update the active logged-in user

    # Ask the user for a username and password
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Record the current time in seconds since the epoch
    current_time = time.time()

    # If this user has not attempted login before, initialise their counters
    if username not in failed_attempts:
        failed_attempts[username] = 0

    if username not in login_attempt_history:
        login_attempt_history[username] = []

    # Add this login attempt time to the user's history
    login_attempt_history[username].append(current_time)

    # Keep only attempts made in the last 60 seconds
    login_attempt_history[username] = [
        attempt_time
        for attempt_time in login_attempt_history[username]
        if current_time - attempt_time <= 60
    ]

    # Detect suspicious repeated login attempts within 60 seconds
    if len(login_attempt_history[username]) > 3:
        print("Warning: Suspicious repeated login attempts detected.")
        log_event(f"Suspicious repeated login attempts detected for user '{username}'")

    # If the account is already locked after 3 failed attempts, block login
    if failed_attempts[username] >= 3:
        print("Account locked due to multiple failed login attempts.")
        log_event(f"Locked account access attempt for user '{username}'")
        return

    # Check whether the supplied credentials are valid
    if username in USERS and USERS[username] == password:
        # Mark the user as logged in
        logged_in_user = username

        # Reset failed attempts after a successful login
        failed_attempts[username] = 0

        print("Login successful.")
        log_event(f"Successful login for user '{username}'")
    else:
        # Increment the failed login counter for this user
        failed_attempts[username] += 1

        print("Invalid username or password.")
        log_event(f"Failed login attempt for user '{username}'")

        # If this is the third failed attempt, lock the account
        if failed_attempts[username] >= 3:
            print("Account locked due to multiple failed login attempts.")
            log_event(f"Account locked after 3 failed attempts for user '{username}'")
            
def calculate_file_hash(file_path):
    # Create a SHA-256 hash object.
    # Python's hashlib module provides SHA-256 as a secure hash algorithm.
    file_hash = hashlib.sha256()

    # Open the file in binary read mode so all bytes are processed correctly.
    with open(file_path, "rb") as file:
        # Read the file in chunks to support larger files efficiently.
        while chunk := file.read(4096):
            # Update the hash with each chunk of file data.
            file_hash.update(chunk)

    # Return the final hexadecimal hash string.
    return file_hash.hexdigest()


def submit_exam_file():
    global logged_in_user  # Access the active logged-in user

    # Prevent file submission if no user is logged in.
    if logged_in_user is None:
        print("You must log in before submitting an exam file.")
        log_event("Blocked file submission attempt without login")
        return

    # Ask the user to enter the path of the file they want to submit.
    file_path = input("Enter the file path of the exam submission: ").strip()

    # Check that the file actually exists.
    if not os.path.isfile(file_path):
        print("Error: file does not exist.")
        log_event(f"Submission rejected for user '{logged_in_user}': file not found")
        return

    # Extract the filename only, without the full directory path.
    file_name = os.path.basename(file_path)

    # Extract the file extension and convert it to lowercase.
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()

    # Validate the file type against the allowed extensions.
    if file_extension not in ALLOWED_EXTENSIONS:
        print("Error: only .pdf and .docx files are allowed.")
        log_event(
            f"Submission rejected for user '{logged_in_user}': invalid file type '{file_extension}'"
        )
        return

    # Check the file size in bytes.
    file_size = os.path.getsize(file_path)

    # Reject files larger than 5 MB.
    if file_size > MAX_FILE_SIZE:
        print("Error: file size exceeds the 5 MB limit.")
        log_event(
            f"Submission rejected for user '{logged_in_user}': file '{file_name}' exceeded 5 MB"
        )
        return

    # Calculate the SHA-256 hash of the file to detect duplicate content.
    file_hash = calculate_file_hash(file_path)

    # Track whether a duplicate has been found.
    duplicate_found = False

    # If the submission record file exists, compare this file against prior submissions.
    if os.path.exists(SUBMISSION_RECORD_FILE):
        with open(SUBMISSION_RECORD_FILE, "r") as record_file:
            for line in record_file:
                # Ignore empty lines.
                if not line.strip():
                    continue

                # Stored format:
                # username,filename,filehash,timestamp
                stored_user, stored_filename, stored_hash, stored_time = line.strip().split(",", 3)

                # Reject only if both the filename and file content are identical.
                if stored_filename == file_name and stored_hash == file_hash:
                    duplicate_found = True
                    break

    # Stop the submission if an identical filename and identical content already exist.
    if duplicate_found:
        print("Error: duplicate submission detected.")
        log_event(
            f"Duplicate submission rejected for user '{logged_in_user}': file '{file_name}'"
        )
        return

    # Record the successful submission in the submission record file.
    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SUBMISSION_RECORD_FILE, "a") as record_file:
        record_file.write(
            f"{logged_in_user},{file_name},{file_hash},{submission_time}\n"
        )

    # Inform the user that the submission succeeded.
    print(f"File '{file_name}' submitted successfully.")

    # Log the successful submission event.
    log_event(
        f"Successful submission by user '{logged_in_user}': "
        f"file '{file_name}', size={file_size} bytes"
    )


def view_submission_log():
    # Try to open and display the log file contents
    try:
        with open(LOG_FILE, "r") as log:
            contents = log.read().strip()

        if not contents:
            print("No log entries found.")
            return

        print("\n========== SUBMISSION LOG ==========")
        print(contents)

    except FileNotFoundError:
        print("No submission log file found.")


while True:
    # Show the menu each time the loop runs
    show_menu()

    # Ask the user to select a menu option
    choice = input("Select an option: ").strip()

    if choice == "1":
        # Run the login system
        login()

    elif choice == "2":
        # Run the submission function
        submit_exam_file()

    elif choice == "3":
        # Display the submission log
        view_submission_log()

    elif choice == "4":
        # Exit the program
        print("Goodbye.")
        log_event("Secure exam submission system exited")
        break

    else:
        # Handle invalid menu selections
        print("Invalid option")