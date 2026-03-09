from datetime import datetime        # Import the datetime class to generate timestamps for log entries (Lutz, 2013)
import time                          # Import time module to simulate execution delays in scheduling algorithms


QUEUE_FILE = "job_queue.txt"        # File used to store all pending jobs waiting to be scheduled
COMPLETED_FILE = "completed_jobs.txt" # File used to store jobs that have finished execution
LOG_FILE = "scheduler_log.txt"       # File used to record system events for monitoring and auditing


def log_event(message):              # Define a function that records scheduler activity in a log file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Generate a timestamp in readable format
    with open(LOG_FILE, "a") as log:  # Open the log file in append mode so previous logs are preserved
        log.write(f"{timestamp} : {message}\n")  # Write the timestamp and message to the log file


def show_menu():                     # Function responsible for displaying the scheduler menu interface
    print("\n========== HPC JOB SCHEDULER ==========")  # Display system title
    print("1. View pending Jobs")   # Menu option allowing the user to see queued jobs
    print("2. Submit Job")          # Menu option allowing the user to add a new job
    print("3. Run Round-Robin Scheduler")  # Menu option to execute the Round Robin scheduling algorithm
    print("4. Run Priority Scheduler")     # Menu option to execute the Priority scheduling algorithm
    print("5. View Completed Jobs")        # Menu option allowing the user to see completed jobs
    print("6. Exit")               # Menu option allowing the user to exit the program
    print("=" * 39)                # Print a divider line for readability


def view_pending_jobs():            # Function used to display all jobs waiting in the queue
    print("\n========== Pending Jobs ==========")  # Section title

    try:                             # Begin error handling block in case the queue file does not exist
        with open(QUEUE_FILE, "r") as queue:  # Open the queue file in read mode
            jobs = [line.strip() for line in queue if line.strip()]  # Read each non-empty line into a list

            if not jobs:            # Check if the queue file contains no jobs
                print("No jobs currently in the queue.")  # Inform the user the queue is empty
                return              # Exit the function

            for index, job in enumerate(jobs, start=1):  # Loop through each stored job with numbering
                student_id, job_name, priority, execution_time = job.split(",")  # Split stored job data
                print(               # Display job information in a structured format
                    f"{index}. Student ID: {student_id} | "
                    f"Job Name: {job_name} | "
                    f"Execution Time: {execution_time}s |"
                    f"Priority: {priority}"
                )

    except FileNotFoundError:        # If the queue file does not exist
        print("Error: job queue file not found.")  # Display an error message


def submit_jobs():                   # Function used to collect and store new job requests
    print("\n========== Submit Job ==========")  # Section title

    student_id = input("Enter student ID: ").strip()  # Request student ID and remove whitespace
    job_name = input("Enter job name: ").strip()      # Request job name and remove whitespace

    try:                                              # Attempt to convert user input into integers
        execution_time = int(input("Enter estimated execution time (in seconds): ").strip())  # Job runtime
        priority = int(input("Enter job priority (1-10): ").strip())  # Job priority value
    except ValueError:                                # Handle invalid numeric input
        print("Error: execution time and priority must be numeric values.")  # Display validation error
        log_event("Failed job submission due to invalid input")  # Log the failure
        return                                        # Exit the function

    if not student_id or not job_name:                # Validate required text fields
        print("Error: student ID and job name cannot be empty.")  # Display error
        log_event("Failed job submission due to empty fields")  # Record error in log
        return

    if execution_time <= 0:                           # Ensure runtime is greater than zero
        print("Error: execution time must be greater than 0.")  # Display validation message
        log_event(f"Invalid execution time entered for job {job_name}")  # Log invalid value
        return

    if priority < 1 or priority > 10:                 # Ensure priority falls within allowed range
        print("Error: priority must be between 1 and 10.")  # Inform user of valid range
        log_event(f"Invalid priority entered for job {job_name}")  # Log invalid value
        return

    with open(QUEUE_FILE, "a") as queue:              # Open queue file in append mode
        queue.write(f"{student_id},{job_name},{priority},{execution_time}\n")  # Save job record

    print(f"Job '{job_name}' submitted successfully!")  # Inform the user submission succeeded

    log_event(                                        # Record job submission event
        f"Student {student_id} submitted job '{job_name}' "
        f"(priority={priority}, execution_time={execution_time}s)"
    )


def run_round_robin():                                # Function implementing Round Robin scheduling
    print("\n========== ROUND ROBIN SCHEDULER ==========")  # Section title

    quantum = 5                                       # Define fixed time quantum for Round Robin scheduling (5 seconds)

    try:
        with open(QUEUE_FILE, "r") as queue:           # Open queue file
            jobs = [line.strip().split(",") for line in queue if line.strip()]  # Load job list

        if not jobs:                                   # Check if queue is empty
            print("No jobs available in the queue.")   # Notify user
            log_event("Round Robin attempted with empty queue")  # Log event
            return

    except FileNotFoundError:                          # Handle missing file
        print("Error: job queue file not found.")
        log_event("Round Robin failed: queue file not found")
        return

    updated_queue = []                                 # List for unfinished jobs

    while jobs:                                        # Continue processing until queue is empty
        current_job = jobs.pop(0)                      # Remove first job from queue

        student_id = current_job[0]                    # Extract student ID
        job_name = current_job[1]                      # Extract job name
        priority = current_job[2]                      # Extract priority
        execution_time = int(current_job[3])           # Extract execution time

        run_time = min(quantum, execution_time)        # Determine execution slice
        remaining_time = execution_time - run_time     # Calculate remaining execution time

        print(                                         # Display job execution information
            f"Running job '{job_name}' for {run_time} seconds "
            f"(Student ID: {student_id}, Priority: {priority})"
        )

        log_event(                                     # Record execution event
            f"Round Robin: ran job '{job_name}' for {run_time}s "
            f"(Student {student_id}, Priority {priority})"
        )

        time.sleep(1)                                  # Simulate job processing delay

        if remaining_time > 0:                         # If job is not finished
            print(f"Job '{job_name}' has {remaining_time} seconds remaining.")  # Inform user
            updated_queue.append([student_id, job_name, priority, str(remaining_time)])  # Requeue job
        else:                                          # If job finished during this cycle
            print(f"Job '{job_name}' completed.")      # Display completion message
            with open(COMPLETED_FILE, "a") as completed:  # Open completed jobs file
                completed.write(f"{student_id},{job_name},{priority},{execution_time}\n")  # Save job

            log_event(                                 # Log job completion
                f"Round Robin: completed job '{job_name}' "
                f"(Student {student_id}, Priority {priority})"
            )

    with open(QUEUE_FILE, "w") as queue:               # Rewrite queue file with unfinished jobs
        for job in updated_queue:                      # Loop through remaining jobs
            queue.write(",".join(job) + "\n")          # Save remaining jobs

    print("Round Robin scheduling cycle complete.")   # Inform user scheduler finished


def run_priority():                                    # Function implementing Priority Scheduling
    print("\n========== PRIORITY SCHEDULER ==========")  # Section title

    try:
        with open(QUEUE_FILE, "r") as queue:           # Open queue file
            jobs = [line.strip().split(",") for line in queue if line.strip()]  # Load job list

        if not jobs:                                   # Check for empty queue
            print("No jobs available in the queue.")
            log_event("Priority scheduling attempted with empty queue")
            return

    except FileNotFoundError:
        print("Error: job queue file not found.")
        log_event("Priority scheduling failed: queue file not found")
        return

    jobs.sort(key=lambda job: int(job[2]), reverse=True)  # Sort jobs by priority (highest first)

    for job in jobs:                                   # Process each job in priority order
        student_id = job[0]
        job_name = job[1]
        priority = int(job[2])
        execution_time = int(job[3])

        print(                                         # Display execution information
            f"Running job '{job_name}' "
            f"(Student ID: {student_id}, Priority: {priority}, Execution Time: {execution_time}s)"
        )

        log_event(                                     # Log job start
            f"Priority Scheduler: started job '{job_name}' "
            f"(Student {student_id}, Priority {priority}, Execution Time {execution_time}s)"
        )

        time.sleep(1)                                  # Simulate execution

        with open(COMPLETED_FILE, "a") as completed:   # Store completed job
            completed.write(f"{student_id},{job_name},{priority},{execution_time}\n")

        log_event(                                     # Log completion
            f"Priority Scheduler: completed job '{job_name}' "
            f"(Student {student_id}, Priority {priority})"
        )

    open(QUEUE_FILE, "w").close()                      # Clear queue file after execution

    print("Priority scheduling complete.")             # Inform user


def view_completed_jobs():                             # Function to display completed job records
    print("\n========== COMPLETED JOBS ==========")

    try:
        with open(COMPLETED_FILE, "r") as completed:
            jobs = [line.strip() for line in completed if line.strip()]

        if not jobs:
            print("No completed jobs found.")
            log_event("Viewed completed jobs - none found")
            return

        for index, job in enumerate(jobs, start=1):    # Display completed jobs
            student_id, job_name, priority, execution_time = job.split(",")
            print(
                f"{index}. Student ID: {student_id} | "
                f"Job Name: {job_name} | "
                f"Priority: {priority} | "
                f"Execution Time: {execution_time}s"
            )

        log_event(f"Viewed completed jobs: {len(jobs)} job(s) listed")

    except FileNotFoundError:
        print("Error: completed jobs file not found.")
        log_event("Failed to view completed jobs: file not found")


while True:                                           # Main program loop keeps scheduler running
    show_menu()                                       # Display menu
    choice = input("Select an option: ")              # Capture user choice

    if choice == "1":                                 # If option 1 selected
        view_pending_jobs()                           # Show pending jobs

    elif choice == "2":                               # If option 2 selected
        submit_jobs()                                 # Submit new job

    elif choice == "3":                               # If option 3 selected
        run_round_robin()                             # Run Round Robin scheduler

    elif choice == "4":                               # If option 4 selected
        run_priority()                                # Run Priority scheduler

    elif choice == "5":                               # If option 5 selected
        view_completed_jobs()                         # Display completed jobs

    elif choice == "6":                               # Exit option
        confirm = input("Are you sure you want to exit? (Y/N): ")
        if confirm.lower() == "y":
            print("Goodbye!")
            log_event("Exited the scheduler")
            break
        else:
            print("Exit cancelled.")
    else:
        print("Invalid option. Please try again.")
        
    
    # References:
    # Lubanovic, B., 2019. Introducing Python: Modern Computing in Simple Packages. 2nd ed. Sebastopol: O’Reilly Media.
    # Lutz, M. (2013). Learning Python. O'Reilly Media, Inc.
    # Ramalho, F. (2022). Fluent Python: Clear, Concise, and Effective Programming. O'Reilly Media.
    # Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). Operating System Concepts (10th ed.). Wiley. 
    # Stallings, W. (2018). Operating Systems: Internals and Design Principles (9th ed.). Pearson.    
    # Note: The above references are included to acknowledge the sources of concepts and code structure used in this implementation.