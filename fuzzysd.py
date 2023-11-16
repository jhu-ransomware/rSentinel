import subprocess
import sys
import re

def run_go_script(directory_path):
    try:
        output = subprocess.check_output(['go', 'run', 'fuzzy.go', directory_path], text=True, stderr=subprocess.STDOUT)
        
        # Use a regular expression to extract the numeric result from the output
        match = re.search(r'Result: (\d+)', output)
        if match:
            result = int(match.group(1))
            return result, None  # Return result and no error
        else:
            return None, f"Error: Could not extract result from output: {output}"
    
    except subprocess.CalledProcessError as e:
        error_message = f"Error: {e.output.strip()}"
        return None, error_message  # Return no result and error message

if __name__ == "__main__":
    # Check if the directory path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/your/directory")
        sys.exit(1)

    # Get the directory path from the command-line argument
    directory_path = sys.argv[1]

    # Call the Go script and capture the result and error message
    result, error_message = run_go_script(directory_path)

    # Check for errors
    if error_message:
        print(error_message)
        sys.exit(1)

    # Print the result
    print(f"Result: {result}")
