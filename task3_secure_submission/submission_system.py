
from datetime import datetime
import os
import hashlib
import time

LOG_FILE = "submission_log.txt"

def log_evet(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"{timestamp} : {message}\n")
        
def show_menu():
    print("\n========== SECURE EXAM SUBMISSION SYSTEM ==========")
    print("1. Login.")
    print("2. Submit Exam File.")
    print("3. View Submission Log.")
    print("4. Exit")
    print("=" * 50) 
    
while True:
    show_menu()
    choice = input("Select an option: ")
    
    if choice == "1":
        print("Login system not implemented yet")
        
    elif choice == "2":
        print("File submission not implemented yet")
        
    elif choice == "3":
        print("View logs not implemented yet")
        
    elif choice == "4":
        print("Goodbye")
        
    else:
        print("Invalid option")