from datetime import datetime

QUEUE_FILE = "job_queue.txt"
COMPLETED_FILE = "completed_jobs.txt"
LOG_FILE = "scheduler_log.txt"

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"{timestamp} : {message}\n")
        
        
def show_menu():
    print("\n========== HPC JOB SCHEDULER ==========")
    print("1. View pending Jobs")
    print("2. Submit Job")
    print("3. Run Round-Robin Scheduler")
    print("4. Run Priority Scheduler")
    print("5. View Completed Jobs")
    print("6. Exit")
    print("="* 39)
    
def view_pending_jobs():
    print("Feature not yet implemented")  # Placeholder for actual implementation
    
def submit_jobs():
    print("Feature not yet implemented")  # Placeholder for actual implementation
    
def run_round_robin():
    print("Feature not yet implemented")  # Placeholder for actual implementation
    
def run_priority():
    print("Feature not yet implemented")  # Placeholder for actual implementation

def view_completed_jobs():
    print("Feature not yet implemented")  # Placeholder for actual implementation

while True:
    show_menu()
    choice = input("Select an option: ")
    
    if choice == "1":
        view_pending_jobs()
    
    elif choice == "2":
        submit_jobs()
        
    elif choice == "3":
        run_round_robin()
        
    elif choice == "4":
        run_priority()
        
    elif choice == "5":
        view_completed_jobs()
        
    elif choice == "6":
        confirm = input("Are you sure you want to exit? (Y/N): ")
        if confirm.lower() == "y":
            print("Goodbye!")
            log_event("Exited the scheduler")
            break
        else:
            print("Exit cancelled.")
    else:
        print("Invalid option. Please try again.")
        