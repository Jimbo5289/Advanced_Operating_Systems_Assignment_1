from datetime import datetime
import time

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
    print("=" * 39)
    
def view_pending_jobs():
    print("\n========== Pending Jobs ==========")
    
    try:
        with open(QUEUE_FILE, "r") as queue:
            jobs = [line.strip() for line in queue if line.strip()]
            
            if not jobs:
                print("No jobs currently in the queue.")
                return
            
            for index, job in enumerate(jobs, start=1):
                student_id, job_name, priority, execution_time = job.split(",")
                print(
                    f"{index}. Student ID: {student_id} | "
                    f"Job Name: {job_name} | "
                    f"Execution Time: {execution_time}s |"
                    f"Priority: {priority}"
                )
                
    except FileNotFoundError:
        print("Error: job queue file not found.")
        
        
def submit_jobs():
    print("\n========== Submit Job ==========")
    
    student_id = input("Enter student ID: ").strip()
    job_name = input("Enter job name: ").strip()
    
    try: 
        execution_time = int(input("Enter estimated execution time (in seconds): ").strip())
        priority = int(input("Enter job priority (1-10): ").strip())
    except ValueError:
        print("Error: execution time and priority must be numeric values.")
        log_event("Failed job submission due to invalid input")
        return
    
    if not student_id or not job_name:
        print("Error: student ID and job name cannot be empty.")
        log_event("Failed job submission due to empty fields")
        return
    
    if execution_time <= 0:
        print("Error: execution time must be greater than 0.")
        log_event(f"Invalid execution time entered for job {job_name}")
        return
    
    if priority < 1 or priority > 10:
        print("Error: priority must be between 1 and 10.")
        log_event(f"Invalid priority entered for job {job_name}")
        return
    
    with open(QUEUE_FILE, "a") as queue:
        queue.write(f"{student_id},{job_name},{priority},{execution_time}\n")
        
    print(f"Job '{job_name}' submitted successfully!")
    log_event(
        f"Student {student_id} submitted job '{job_name}' "
        f"(priority={priority}, execution_time={execution_time}s)"
    )
    
    
def run_round_robin():
    print("\n========== ROUND ROBIN SCHEDULER ==========")

    quantum = 5

    try:
        with open(QUEUE_FILE, "r") as queue:
            jobs = [line.strip().split(",") for line in queue if line.strip()]

        if not jobs:
            print("No jobs available in the queue.")
            log_event("Round Robin attempted with empty queue")
            return

    except FileNotFoundError:
        print("Error: job queue file not found.")
        log_event("Round Robin failed: queue file not found")
        return

    updated_queue = []

    while jobs:
        current_job = jobs.pop(0)

        student_id = current_job[0]
        job_name = current_job[1]
        priority = current_job[2]
        execution_time = int(current_job[3])

        run_time = min(quantum, execution_time)
        remaining_time = execution_time - run_time

        print(
            f"Running job '{job_name}' for {run_time} seconds "
            f"(Student ID: {student_id}, Priority: {priority})"
        )

        log_event(
            f"Round Robin: ran job '{job_name}' for {run_time}s "
            f"(Student {student_id}, Priority {priority})"
        )

        time.sleep(1)  # Simulate job execution (replace with actual processing in real implementation)

        if remaining_time > 0:
            print(f"Job '{job_name}' has {remaining_time} seconds remaining.")
            updated_queue.append([student_id, job_name, priority, str(remaining_time)])
        else:
            print(f"Job '{job_name}' completed.")
            with open(COMPLETED_FILE, "a") as completed:
                completed.write(f"{student_id},{job_name}, {priority}, {execution_time}\n")

            log_event(
                f"Round Robin: completed job '{job_name}' "
                f"(Student {student_id}, Priority {priority})"
            )

    with open(QUEUE_FILE, "w") as queue:
        for job in updated_queue:
            queue.write(",".join(job) + "\n")

    print("Round Robin scheduling cycle complete.")
    
    
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
        