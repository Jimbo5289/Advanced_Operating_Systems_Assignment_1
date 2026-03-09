#!/bin/bash

LOGFILE="system_monitor_log.txt"
ARCHIVE_DIR="ArchiveLogs"

log_action() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') : $1" >> "$LOGFILE"
}

show_menu() {
    echo ""
    echo "======================================="
    echo " University Data Centre Admin System"
    echo "======================================="
    echo "1. Display CPU and Memory Usage"
    echo "2. Show Top 10 Memory Processes"
    echo "3. Terminate a Process"
    echo "4. Inspect Disk Usage"
    echo "5. Archive Large Log Files"
    echo "6. Exit"
    echo "======================================="
}

show_usage() {

    echo ""
    echo "========== CPU AND MEMORY USAGE =========="

    top -l 1 | head -n 10

    echo "=========================================="

    log_action "Viewed CPU and memory usage"

}

top_processes() {
    echo ""
    echo "========== TOP 10 MEMORY PROCESSES =========="

    ps aux | sort -nrk 4 | head -n 10 | awk '{printf "PID: %-8ss | User: %-15s | CPU: %-8s | Memory: %-8s | COMMAND: %s\n", $2, $1, $3, $4, $11}'

    echo "=========================================="

    log_action "Viewed top 10 memory consuming processes"
}

kill_process() {

    echo ""
    echo "========== TERMINATE A PROCESS =========="

    read -p "Enter the PID of the process to terminate: " pid

    # Check if input is numeric
    if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo "Error: PID must be a numeric value."
        log_action "Invalid PID entered for termination: $pid"
        return
    fi

    # Check if process exists
    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo "Error: No process found with PID $pid."
        log_action "Attempted termination of non-existent PID: $pid"
        return
    fi

    # Protect critical system processes
    if [[ "$pid" -eq 1 || "$pid" -eq $$ || "$pid" -eq $PPID ]]; then
        echo "Error: Critical system or current shell process cannot be terminated."
        log_action "Blocked termination attempt on protected PID: $pid"
        return
    fi

    # Show process info before confirmation
    echo ""
    echo "Process details:"
    ps -p "$pid" -o pid=,user=,%cpu=,%mem=,comm=

    echo ""
    read -p "Are you sure you want to terminate this process? (Y/N): " confirm

    if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
        kill "$pid" 2>/dev/null

        if [[ $? -eq 0 ]]; then
            echo "Process $pid terminated successfully."
            log_action "Terminated process PID $pid"
        else
            echo "Error: Failed to terminate process $pid."
            log_action "Failed to terminate process PID $pid"
        fi
    else
        echo "Termination cancelled."
        log_action "Cancelled termination for PID $pid"
    fi

    echo "========================================="

}

disk_check() {

    echo ""
    echo "========== DISK USAGE INSPECTION =========="

    read -p "Enter the directory path to inspect: " dir_path

    # Check if directory exists
    if [[ ! -d "$dir_path" ]]; then
        echo "Error: Directory does not exist."
        log_action "Invalid directory entered for disk inspection: $dir_path"
        return
    fi

    echo ""
    echo "Disk usage for $dir_path:"
    du -sh "$dir_path"

    echo "==========================================="

    log_action "Inspected disk usage for directory: $dir_path"
}

archive_logs() {

    echo ""
    echo "========== LOG ARCHIVING SYSTEM =========="

    # Create archive directory if it does not exist
    if [[ ! -d "$ARCHIVE_DIR" ]]; then
        mkdir -p "$ARCHIVE_DIR"
        echo "Created archive directory: $ARCHIVE_DIR"
        log_action "Created archive directory: $ARCHIVE_DIR"
    fi

    found_logs=false

    # Search for .log files larger than 50MB in current directory and subdirectories
    while IFS= read -r file
    do
        found_logs=true

        timestamp=$(date '+%Y%m%d_%H%M%S')
        base_name=$(basename "$file" .log)
        archive_name="${ARCHIVE_DIR}/${base_name}_${timestamp}.log.gz"

        gzip -c "$file" > "$archive_name"

        echo "Archived: $file -> $archive_name"
        log_action "Archived log file: $file to $archive_name"

    done < <(find . -type f -name "*.log" -size +50M)

    if [[ "$found_logs" == false ]]; then
        echo "No log files larger than 50MB were found."
        log_action "No large log files found for archiving"
    fi

    # Check ArchiveLogs size and warn if over 1GB
    archive_size_kb=$(du -sk "$ARCHIVE_DIR" | awk '{print $1}')
    archive_size_mb=$((archive_size_kb / 1024))

    if [[ "$archive_size_kb" -gt 1048576 ]]; then
        echo "WARNING: $ARCHIVE_DIR exceeds 1GB."
        log_action "Warning: $ARCHIVE_DIR exceeds 1GB"
    else
        echo "$ARCHIVE_DIR size: ${archive_size_mb}MB"
    fi

    echo "========================================="

}

while true
do
    show_menu
    read -p "Select an option: " choice

    case $choice in
        1) show_usage ;;
        2) top_processes ;;
        3) kill_process ;;
        4) disk_check ;;
        5) archive_logs ;;
        6)
            read -p "Are you sure you want to exit? (Y/N): " confirm
            if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
                log_action "Exited system"
                echo "Goodbye."
                exit
            fi
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
done