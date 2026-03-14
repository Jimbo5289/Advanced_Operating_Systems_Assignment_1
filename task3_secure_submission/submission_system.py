from datetime import datetime  # Import datetime so timestamps can be written to log records
import os                      # Import os for file/path checks and directory creation
import hashlib                 # Import hashlib for SHA-256 password and file hashing
import time                    # Import time for repeated login-attempt tracking
import shutil                  # Import shutil so submitted files can be copied securely

# File used to record login events, suspicious activity, and submission activity
LOG_FILE = "submission_log.txt"

# File used to store successful submission records
SUBMISSION_RECORD_FILE = "submitted_files.txt"

# File used to store registered usernames and hashed passwords
USER_DB_FILE = "users.txt"

# Maximum allowed submission size set to 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Only these file types are allowed for submission
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

# Directory used to store accepted submissions securely
SUBMISSION_DIR = "exam_submissions"

# Create the secure submission directory if it does not already exist
if not os.path.exists(SUBMISSION_DIR):
    os.makedirs(SUBMISSION_DIR)

# Track the currently logged-in user
logged_in_user = None

# Track failed login attempts for each username
failed_attempts = {}

# Track recent login attempt timestamps for each username
login_attempt_history = {}


def log_event(message):
    # Create a timestamp in year-month-day hour:minute:second format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode so older records remain
    with open(LOG_FILE, "a") as log:
        # Write the timestamp and message to the log file
        log.write(f"{timestamp} : {message}\n")


def hash_password(password):
    # Convert the plain-text password into a SHA-256 hexadecimal hash
    return hashlib.sha256(password.encode()).hexdigest()


def show_menu():
    global logged_in_user

    # Display the main system menu
    print("\n========== SECURE EXAM SUBMISSION SYSTEM ==========")
    print("1. Register User")
    print("2. Login")
    print("3. Logout")
    print("4. Submit Exam File")
    print("5. Check if File Already Submitted")
    print("6. List All Submitted Assignments")
    print("7. View Submission Log")
    print("8. Exit")
    print("=" * 50)

    # Display which user is currently logged in
    if logged_in_user is not None:
        print(f"Current user: {logged_in_user}")
    else:
        print("Current user: None")


def register_user():
    # Display a heading for the registration section
    print("\n========== USER REGISTRATION ==========")

    # Ask the user to choose a username
    username = input("Choose a username: ").strip()

    # Ask the user to choose a password
    password = input("Choose a password: ").strip()

    # Reject empty username or password input
    if not username or not password:
        print("Username and password cannot be empty.")
        log_event("Failed registration attempt due to empty username or password")
        return

    # If the user database file already exists, check for duplicate usernames
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as user_db:
            for line in user_db:
                # Skip blank lines if present
                if not line.strip():
                    continue

                # Split each stored user record into username and hashed password
                stored_user, _ = line.strip().split(",", 1)

                # Reject the registration if the username already exists
                if stored_user == username:
                    print("Username already exists.")
                    log_event(f"Failed registration attempt: username '{username}' already exists")
                    return

    # Convert the password into a SHA-256 hash before storing it
    password_hash = hash_password(password)

    # Open the user database file in append mode
    with open(USER_DB_FILE, "a") as user_db:
        # Store the username and hashed password
        user_db.write(f"{username},{password_hash}\n")

    # Inform the user that registration succeeded
    print("User registered successfully.")

    # Record the registration event in the log
    log_event(f"New user registered: {username}")


def login():
    global logged_in_user  # Allow this function to update the current login session

    # Prevent repeated login if a user is already signed in
    if logged_in_user is not None:
        print(f"User '{logged_in_user}' is already logged in.")
        log_event(
            f"Blocked repeated login attempt while user '{logged_in_user}' was already signed in"
        )
        return

    # Ask the user for their username
    username = input("Enter username: ").strip()

    # Ask the user for their password
    password = input("Enter password: ").strip()

    # Convert the password into a SHA-256 hash for comparison
    password_hash = hash_password(password)

    # Record the current time for suspicious-attempt tracking
    current_time = time.time()

    # If this username has never failed before, initialise the failed-attempt counter
    if username not in failed_attempts:
        failed_attempts[username] = 0

    # If this username has no prior timing history, initialise an empty list
    if username not in login_attempt_history:
        login_attempt_history[username] = []

    # Add this login attempt time to the user's history
    login_attempt_history[username].append(current_time)

    # Keep only login attempts made within the last 60 seconds
    login_attempt_history[username] = [
        attempt_time
        for attempt_time in login_attempt_history[username]
        if current_time - attempt_time <= 60
    ]

    # Warn if more than 3 login attempts were made within 60 seconds
    if len(login_attempt_history[username]) > 3:
        print("Warning: Suspicious repeated login attempts detected.")
        log_event(f"Suspicious repeated login attempts detected for user '{username}'")

    # Block access if the account has already reached the lock threshold
    if failed_attempts[username] >= 3:
        print("Account locked due to multiple failed login attempts.")
        log_event(f"Locked account access attempt for user '{username}'")
        return

    # Stop if no users have been registered yet
    if not os.path.exists(USER_DB_FILE):
        print("No users are registered yet.")
        log_event("Login attempted before any users were registered")
        return

    # Track whether valid credentials were found
    user_found = False

    # Open the user database file and search for matching credentials
    with open(USER_DB_FILE, "r") as user_db:
        for line in user_db:
            # Skip blank lines if present
            if not line.strip():
                continue

            # Split the stored record into username and hashed password
            stored_user, stored_hash = line.strip().split(",", 1)

            # Check whether both the username and password hash match
            if stored_user == username and stored_hash == password_hash:
                user_found = True
                break

    # Handle a successful login
    if user_found:
        # Mark this user as the active logged-in user
        logged_in_user = username

        # Reset failed attempts after successful authentication
        failed_attempts[username] = 0

        # Inform the user that login succeeded
        print(f"Login successful. Welcome, {username}.")

        # Record the successful login in the log
        log_event(f"Successful login for user '{username}'")
    else:
        # Increment the failed-attempt counter for this username
        failed_attempts[username] += 1

        # Inform the user that the credentials were invalid
        print("Invalid username or password.")

        # Record the failed login attempt in the log
        log_event(f"Failed login attempt for user '{username}'")

        # Lock the account after 3 failed attempts
        if failed_attempts[username] >= 3:
            print("Account locked due to multiple failed login attempts.")
            log_event(f"Account locked after 3 failed attempts for user '{username}'")


def logout():
    global logged_in_user  # Allow this function to clear the active user

    # Prevent logout if no one is currently signed in
    if logged_in_user is None:
        print("No user is currently logged in.")
        log_event("Blocked logout attempt with no active user")
        return

    # Store the current username before clearing it
    user_to_log_out = logged_in_user

    # Clear the active session
    logged_in_user = None

    # Inform the user that logout succeeded
    print(f"User '{user_to_log_out}' has been logged out.")

    # Record the logout event
    log_event(f"User '{user_to_log_out}' logged out")


def calculate_file_hash(file_path):
    # Create a SHA-256 hash object for duplicate file detection
    file_hash = hashlib.sha256()

    # Open the file in binary mode so all bytes are processed correctly
    with open(file_path, "rb") as file:
        # Read the file in 4096-byte chunks until the end is reached
        while chunk := file.read(4096):
            # Update the hash with each chunk of data
            file_hash.update(chunk)

    # Return the final hexadecimal digest string
    return file_hash.hexdigest()


def submit_exam_file():
    global logged_in_user  # Access the active logged-in user

    # Prevent file submission unless a user is logged in
    if logged_in_user is None:
        print("You must log in before submitting an exam file.")
        log_event("Blocked file submission attempt without login")
        return

    # Ask the user for the path of the file they want to submit
    file_path = input("Enter the file path of the exam submission: ").strip()

    # Check that the submitted path points to an existing file
    if not os.path.isfile(file_path):
        print("Error: file does not exist.")
        log_event(f"Submission rejected for user '{logged_in_user}': file not found")
        return

    # Extract the file name from the path
    file_name = os.path.basename(file_path)

    # Extract the extension from the file name
    _, file_extension = os.path.splitext(file_name)

    # Convert the extension to lowercase for consistent validation
    file_extension = file_extension.lower()

    # Reject the file if it is not an allowed extension
    if file_extension not in ALLOWED_EXTENSIONS:
        print("Error: only .pdf and .docx files are allowed.")
        log_event(
            f"Submission rejected for user '{logged_in_user}': invalid file type '{file_extension}'"
        )
        return

    # Determine the file size in bytes
    file_size = os.path.getsize(file_path)

    # Reject the file if it exceeds the 5 MB size limit
    if file_size > MAX_FILE_SIZE:
        print("Error: file size exceeds the 5 MB limit.")
        log_event(
            f"Submission rejected for user '{logged_in_user}': file '{file_name}' exceeded 5 MB"
        )
        return

    # Calculate a SHA-256 hash of the file contents
    file_hash = calculate_file_hash(file_path)

    # Track whether an identical submission already exists
    duplicate_found = False

    # If previous submissions exist, compare the file name and file hash
    if os.path.exists(SUBMISSION_RECORD_FILE):
        with open(SUBMISSION_RECORD_FILE, "r") as record_file:
            for line in record_file:
                # Skip blank lines
                if not line.strip():
                    continue

                # Split the stored record into username, filename, hash, and timestamp
                stored_user, stored_filename, stored_hash, stored_time = line.strip().split(",", 3)

                # Mark as duplicate only if both file name and content hash match
                if stored_filename == file_name and stored_hash == file_hash:
                    duplicate_found = True
                    break

    # Reject the submission if it is a duplicate
    if duplicate_found:
        print("Error: duplicate submission detected.")
        log_event(
            f"Duplicate submission rejected for user '{logged_in_user}': file '{file_name}'"
        )
        return

    # Create a timestamp for secure stored naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build a unique filename to avoid overwriting prior submissions
    secure_filename = f"{logged_in_user}_{timestamp}_{file_name}"

    # Create the destination path inside the secure submissions directory
    destination_path = os.path.join(SUBMISSION_DIR, secure_filename)

    # Copy the submitted file into the secure storage directory
    shutil.copy(file_path, destination_path)

    # Create a readable submission timestamp for the record file
    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store the successful submission record
    with open(SUBMISSION_RECORD_FILE, "a") as record_file:
        record_file.write(
            f"{logged_in_user},{file_name},{file_hash},{submission_time}\n"
        )

    # Inform the user that submission succeeded
    print(f"File '{file_name}' submitted successfully.")

    # Record the successful submission event
    log_event(
        f"Successful submission by user '{logged_in_user}': "
        f"file '{file_name}' stored as '{secure_filename}'"
    )
    
def check_existing_submission():
    # Prevent unauthorised access to submission records
    if logged_in_user is None:
        print("You must log in before checking submissions.")
        log_event("Blocked submission check attempt without login")
        return

    # Ask the user for the file path they want to check
    file_path = input("Enter the file path to check: ").strip()

    # Check that the file exists
    if not os.path.isfile(file_path):
        print("Error: file does not exist.")
        log_event(f"Submission check failed for user '{logged_in_user}': file not found")
        return

    # Extract the file name from the path
    file_name = os.path.basename(file_path)

    # Calculate the SHA-256 hash of the file
    file_hash = calculate_file_hash(file_path)

    # If no submission record file exists yet, then nothing has been submitted
    if not os.path.exists(SUBMISSION_RECORD_FILE):
        print("No submissions have been recorded yet.")
        log_event(f"Submission check performed by user '{logged_in_user}': no records exist")
        return

    # Track whether a matching submission was found
    match_found = False

    # Open the submission record file and compare name/hash pairs
    with open(SUBMISSION_RECORD_FILE, "r") as record_file:
        for line in record_file:
            if not line.strip():
                continue

            stored_user, stored_filename, stored_hash, stored_time = line.strip().split(",", 3)

            # Match only if both filename and content hash are the same
            if stored_filename == file_name and stored_hash == file_hash:
                match_found = True
                print(
                    f"File '{file_name}' has already been submitted "
                    f"by user '{stored_user}' on {stored_time}."
                )
                log_event(
                    f"Submission check matched existing file '{file_name}' for user '{logged_in_user}'"
                )
                break

    # Inform the user if no identical submission exists
    if not match_found:
        print(f"File '{file_name}' has not been submitted before.")
        log_event(
            f"Submission check found no prior match for file '{file_name}' by user '{logged_in_user}'"
        )
        
def list_submitted_assignments():
    # Prevent unauthorised access to submission records
    if logged_in_user is None:
        print("You must log in before listing submitted assignments.")
        log_event("Blocked list submissions attempt without login")
        return

    # If there is no submission record file yet, report that clearly
    if not os.path.exists(SUBMISSION_RECORD_FILE):
        print("No submitted assignments found.")
        log_event(f"List submissions requested by user '{logged_in_user}': no records exist")
        return

    # Read all non-empty submission records
    with open(SUBMISSION_RECORD_FILE, "r") as record_file:
        records = [line.strip() for line in record_file if line.strip()]

    # If the file exists but is empty, report that
    if not records:
        print("No submitted assignments found.")
        log_event(f"List submissions requested by user '{logged_in_user}': file empty")
        return

    # Display all submission records in a readable format
    print("\n========== SUBMITTED ASSIGNMENTS ==========")

    for index, record in enumerate(records, start=1):
        submitted_user, submitted_filename, submitted_hash, submitted_time = record.split(",", 3)
        print(
            f"{index}. User: {submitted_user} | "
            f"File: {submitted_filename} | "
            f"Submitted: {submitted_time}"
        )

    print("=" * 50)

    # Record the viewing action in the system log
    log_event(
        f"Listed submitted assignments for user '{logged_in_user}': {len(records)} record(s) shown"
    )

def view_submission_log():
    # Prevent unauthorised users from viewing the log
    if logged_in_user is None:
        print("You must log in before viewing the submission log.")
        log_event("Blocked attempt to view submission log without login")
        return

    try:
        # Open the log file and read all contents
        with open(LOG_FILE, "r") as log:
            contents = log.read().strip()

        # Inform the user if the log exists but has no entries
        if not contents:
            print("No log entries found.")
            return

        # Display the contents of the submission log
        print("\n========== SUBMISSION LOG ==========")
        print(contents)
        print("=" * 50)

    except FileNotFoundError:
        # Handle the case where the log file does not yet exist
        print("No submission log file found.")


while True:
    # Display the menu at the start of each loop cycle
    show_menu()

    # Ask the user to select a menu option
    choice = input("Select an option: ").strip()

    # Run the registration function if option 1 is selected
    if choice == "1":
        register_user()

    # Run the login function if option 2 is selected
    elif choice == "2":
        login()

    # Run the logout function if option 3 is selected
    elif choice == "3":
        logout()

    # Run the submission function if option 4 is selected
    elif choice == "4":
        submit_exam_file()

    # Check whether a file has already been submitted
    elif choice == "5":
        check_existing_submission()

    # List all submitted assignments
    elif choice == "6":
        list_submitted_assignments()

    # Display the submission log if option 7 is selected
    elif choice == "7":
        view_submission_log()

    # Exit the program if option 8 is selected
    elif choice == "8":
        print("Goodbye.")
        log_event("Secure exam submission system exited")
        break

    # Handle invalid menu selections
    else:
        print("Invalid option")
        log_event(f"Invalid menu selection: '{choice}'")