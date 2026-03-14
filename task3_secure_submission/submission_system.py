from datetime import datetime  # Import datetime so timestamps can be added to log records
import os                      # Import os for file and path checking
import hashlib                 # Import hashlib for SHA-256 duplicate detection
import time                    # Import time for tracking repeated login attempts
import shutil                  # Import shutil so submitted files can be copied securely

# Store the file name used for general system logging
LOG_FILE = "submission_log.txt"

# Store the file name used to record successful submissions
SUBMISSION_RECORD_FILE = "submitted_files.txt"

# Set the maximum allowed file size to 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Define the only file extensions accepted by the system
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

# Define the directory where accepted submissions will be stored
SUBMISSION_DIR = "exam_submissions"

# Create the secure submission directory if it does not already exist
if not os.path.exists(SUBMISSION_DIR):
    os.makedirs(SUBMISSION_DIR)

# Create a simple dictionary of valid usernames and passwords
# In a real system, passwords would be hashed and stored securely
USERS = {
    "student1": "password123",
    "student2": "securepass456"
}

# Track the user who is currently logged in
logged_in_user = None

# Track how many failed login attempts each user has made
failed_attempts = {}

# Track recent login attempt times for each user
login_attempt_history = {}


def log_event(message):
    # Create a timestamp for the log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode so existing records are preserved
    with open(LOG_FILE, "a") as log:
        # Write the timestamp and event message to the log file
        log.write(f"{timestamp} : {message}\n")


def show_menu():
    # Display the main system menu
    print("\n========== SECURE EXAM SUBMISSION SYSTEM ==========")
    print("1. Login")
    print("2. Submit Exam File")
    print("3. View Submission Log")
    print("4. Exit")
    print("=" * 50)


def login():
    # Tell Python that this function will update the logged-in user variable
    global logged_in_user

    # Ask the user for their username
    username = input("Enter username: ").strip()

    # Ask the user for their password
    password = input("Enter password: ").strip()

    # Record the current time in seconds
    current_time = time.time()

    # If the username has not appeared before, initialise its failed-attempt counter
    if username not in failed_attempts:
        failed_attempts[username] = 0

    # If the username has no login history yet, create an empty list
    if username not in login_attempt_history:
        login_attempt_history[username] = []

    # Append the current login attempt time to the user's history
    login_attempt_history[username].append(current_time)

    # Keep only login attempts made within the last 60 seconds
    login_attempt_history[username] = [
        attempt_time
        for attempt_time in login_attempt_history[username]
        if current_time - attempt_time <= 60
    ]

    # Detect suspicious repeated login attempts within 60 seconds
    if len(login_attempt_history[username]) > 3:
        print("Warning: Suspicious repeated login attempts detected.")
        log_event(f"Suspicious repeated login attempts detected for user '{username}'")

    # Prevent access if the account has already been locked
    if failed_attempts[username] >= 3:
        print("Account locked due to multiple failed login attempts.")
        log_event(f"Locked account access attempt for user '{username}'")
        return

    # Check whether the entered credentials match a valid user
    if username in USERS and USERS[username] == password:
        # Mark this user as logged in
        logged_in_user = username

        # Reset failed attempts after a successful login
        failed_attempts[username] = 0

        # Inform the user that login succeeded
        print("Login successful.")

        # Log the successful login
        log_event(f"Successful login for user '{username}'")
    else:
        # Increment the failed-attempt counter for this user
        failed_attempts[username] += 1

        # Inform the user that the login failed
        print("Invalid username or password.")

        # Log the failed login attempt
        log_event(f"Failed login attempt for user '{username}'")

        # Lock the account after three failed attempts
        if failed_attempts[username] >= 3:
            print("Account locked due to multiple failed login attempts.")
            log_event(f"Account locked after 3 failed attempts for user '{username}'")


def calculate_file_hash(file_path):
    # Create a SHA-256 hash object
    file_hash = hashlib.sha256()

    # Open the file in binary mode so its raw contents can be hashed
    with open(file_path, "rb") as file:
        # Read the file in chunks until the end is reached
        while chunk := file.read(4096):
            # Update the hash with each chunk of file data
            file_hash.update(chunk)

    # Return the final hexadecimal digest of the hash
    return file_hash.hexdigest()


def submit_exam_file():
    # Tell Python that this function may read the current logged-in user
    global logged_in_user

    # Prevent submission unless a user is logged in
    if logged_in_user is None:
        print("You must log in before submitting an exam file.")
        log_event("Blocked file submission attempt without login")
        return

    # Ask the user for the file path of the exam file they want to submit
    file_path = input("Enter the file path of the exam submission: ").strip()

    # Check that the file actually exists
    if not os.path.isfile(file_path):
        print("Error: file does not exist.")
        log_event(f"Submission rejected for user '{logged_in_user}': file not found")
        return

    # Extract the file name from the full path
    file_name = os.path.basename(file_path)

    # Separate the extension from the file name
    _, file_extension = os.path.splitext(file_name)

    # Convert the extension to lowercase for consistent validation
    file_extension = file_extension.lower()

    # Reject the file if it is not a PDF or DOCX
    if file_extension not in ALLOWED_EXTENSIONS:
        print("Error: only .pdf and .docx files are allowed.")
        log_event(
            f"Submission rejected for user '{logged_in_user}': invalid file type '{file_extension}'"
        )
        return

    # Check the size of the file in bytes
    file_size = os.path.getsize(file_path)

    # Reject the file if it is larger than 5 MB
    if file_size > MAX_FILE_SIZE:
        print("Error: file size exceeds the 5 MB limit.")
        log_event(
            f"Submission rejected for user '{logged_in_user}': file '{file_name}' exceeded 5 MB"
        )
        return

    # Calculate a SHA-256 hash of the submitted file
    file_hash = calculate_file_hash(file_path)

    # Track whether a duplicate submission has been found
    duplicate_found = False

    # If the submission record file already exists, compare this file against previous submissions
    if os.path.exists(SUBMISSION_RECORD_FILE):
        with open(SUBMISSION_RECORD_FILE, "r") as record_file:
            for line in record_file:
                # Skip empty lines
                if not line.strip():
                    continue

                # Split the stored record into its components
                stored_user, stored_filename, stored_hash, stored_time = line.strip().split(",", 3)

                # Mark as duplicate only if both the file name and file content match
                if stored_filename == file_name and stored_hash == file_hash:
                    duplicate_found = True
                    break

    # Reject the file if it is a duplicate submission
    if duplicate_found:
        print("Error: duplicate submission detected.")
        log_event(
            f"Duplicate submission rejected for user '{logged_in_user}': file '{file_name}'"
        )
        return

    # Create a timestamp to make the stored file name unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build a secure stored file name using username, timestamp, and original file name
    secure_filename = f"{logged_in_user}_{timestamp}_{file_name}"

    # Create the full destination path inside the secure submissions directory
    destination_path = os.path.join(SUBMISSION_DIR, secure_filename)

    # Copy the submitted file into the secure submissions directory
    shutil.copy(file_path, destination_path)

    # Record the submission time for the submission record file
    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store the submission metadata in the submission record file
    with open(SUBMISSION_RECORD_FILE, "a") as record_file:
        record_file.write(
            f"{logged_in_user},{file_name},{file_hash},{submission_time}\n"
        )

    # Inform the user that submission succeeded
    print(f"File '{file_name}' submitted successfully.")

    # Log the successful submission and stored filename
    log_event(
        f"Successful submission by user '{logged_in_user}': "
        f"file '{file_name}' stored as '{secure_filename}'"
    )


def view_submission_log():
    # Prevent unauthorised viewing of the system log
    if logged_in_user is None:
        print("You must log in before viewing the submission log.")
        log_event("Blocked attempt to view submission log without login")
        return

    try:
        # Open the log file and read its contents
        with open(LOG_FILE, "r") as log:
            contents = log.read().strip()

        # If the log file exists but is empty, inform the user
        if not contents:
            print("No log entries found.")
            return

        # Display the submission log contents
        print("\n========== SUBMISSION LOG ==========")
        print(contents)
        print("=" * 50)

    except FileNotFoundError:
        # Handle the case where the log file does not yet exist
        print("No submission log file found.")


while True:
    # Display the menu at the start of each loop cycle
    show_menu()

    # Ask the user to choose a menu option
    choice = input("Select an option: ").strip()

    # Run the login function if option 1 is selected
    if choice == "1":
        login()

    # Run the exam submission function if option 2 is selected
    elif choice == "2":
        submit_exam_file()

    # Run the log viewing function if option 3 is selected
    elif choice == "3":
        view_submission_log()

    # Exit the system if option 4 is selected
    elif choice == "4":
        print("Goodbye.")
        log_event("Secure exam submission system exited")
        break

    # Handle invalid menu selections
    else:
        print("Invalid option")