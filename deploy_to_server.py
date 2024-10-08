import subprocess
import sys
import argparse

# Define the server credentials and app directory on the server
project_dir = "/root/fivestars-appointment-app-flask"

def run_command(command):
    """Helper function to run shell commands and exit on failure."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Running: {command}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")

    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)

def deploy(server_ip, username, password):
    # Step 1: SSH into the server and pull the latest code
    print("SSHing into the server and pulling the latest code...")
    ssh_command = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{server_ip} "cd {project_dir} && git pull origin main"'
    run_command(ssh_command)

    # Step 2: Find the process ID for the Flask server
    print("Finding the Flask server process...")
    ssh_command = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{server_ip} "ps aux | grep \'[p]ython.*fivestars-appointment-app-flask\' | awk \'{{print $2}}\'"'
    result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

    pid = result.stdout.strip()
    if pid:
        # Step 3: Stop the Flask server if a process is found
        print(f"Stopping Flask server with PID {pid}...")
        ssh_command = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{server_ip} "kill -9 {pid}"'
        run_command(ssh_command)
    else:
        print("No Flask server process found. Skipping kill command.")

    # Step 4: Restart the Flask server
    print("Starting the Flask server...")
    ssh_command = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {username}@{server_ip} "cd {project_dir} && source venv_appt/bin/activate && export PYTHONPATH={project_dir} && setsid nohup python3 appointmentapp/run.py > flask.out 2>&1 &"'
    run_command(ssh_command)

    print('Successfully deployed the app.')

if __name__ == "__main__":
    # Setup argparse to get the server_ip, username, and password from the command line
    parser = argparse.ArgumentParser(description="Deploy the Flask app.")
    parser.add_argument('--server_ip', required=True, help='The IP address of the server.')
    parser.add_argument('--username', required=True, help='The username to SSH into the server.')
    parser.add_argument('--password', required=True, help='The password to SSH into the server.')

    # Parse arguments
    args = parser.parse_args()

    # Call the deploy function with command line arguments
    deploy(args.server_ip, args.username, args.password)
