import subprocess
import sys

def run_go_script(directory_path):
    try:
        output = subprocess.check_output(['go', 'run', 'fuzzy.go', directory_path], text=True, stderr=subprocess.STDOUT)
        return int(output.strip())
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.strip()}"

if __name__ == "__main__":
    # Check if the directory path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/your/directory")
        sys.exit(1)

    # Get the directory path from the command-line argument
    directory_path = sys.argv[1]

    # Call the Go script and capture the output
    result = run_go_script("/c/cygwin/cgdrive/Users/")

    # Check if the result is an integer and is either 0 or 1
    if not isinstance(result, int) or result not in [0, 1]:
        raise ValueError(f"Invalid result: {result}. Expected 0 or 1.")