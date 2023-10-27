import os
import logging
import constants

logger = logging.getLogger(__name__)
tracked_magic_numbers = {}

def get_magic_number(filename):
    with open(filename, 'rb') as f:
        return f.read(4)

def save_magic_numbers(files):
    for file in files:
        magic_number = get_magic_number(file)
        tracked_magic_numbers[file] = magic_number.hex()

def check_magic_numbers():
    global tracked_magic_numbers

    files_to_track = [os.path.join(constants.TEST_DIR, file) for file in os.listdir(constants.TEST_DIR) if os.path.isfile(os.path.join(constants.TEST_DIR, file))]
    
    if not tracked_magic_numbers:
        logging.debug("Saving magic numbers for the first time")
        save_magic_numbers(files_to_track)
        logging.info("Magic numbers saved successfully for the first time - {tracked_magic_numbers}")
        return False  # No changes detected on the first run

    changed_files_count = 0
    total_files = len(files_to_track)

    for file in files_to_track:
        current_magic_number = get_magic_number(file).hex()
        if file in tracked_magic_numbers:
            if tracked_magic_numbers[file] != current_magic_number:
                logging.debug(f"WARNING: Magic number for {file} has changed!")
                changed_files_count += 1
            else:
                logging.debug(f"Magic number for {file} remains the same.")
        else:
            logging.debug(f"Magic number for {file} not found in tracked records.")

    return changed_files_count > total_files * 0.5  # Return True if more than 50% of files changed

if __name__ == '__main__':
    result = check_magic_numbers()
    if result:
        logging.debug("More than 50% of the files in the directory have changed file types.")
    else:
        logging.debug("Less than or equal to 50% of the files in the directory have changed file types.")
