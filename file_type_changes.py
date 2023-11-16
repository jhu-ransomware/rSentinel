import os
import constants
from logconfig import get_logger

logger = get_logger(__name__)

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
        logger.debug("Saving magic numbers for the first time")
        save_magic_numbers(files_to_track)
        logger.info(f"Magic numbers saved successfully for the first time - {tracked_magic_numbers}")
        return False  # No changes detected on the first run

    changed_files_count = 0
    total_files = len(files_to_track)

    for file in files_to_track:
        current_magic_number = get_magic_number(file).hex()
        logger.info(f"Newly calculated magic number of {file} - {current_magic_number}")
        if file in tracked_magic_numbers:
            if tracked_magic_numbers[file] != current_magic_number:
                logger.info(f"WARNING: Magic number for {file} has changed to {current_magic_number}")
                changed_files_count += 1
            else:
                logger.debug(f"Magic number for {file} remains the same.")
        else:
            logger.debug(f"Magic number for {file} not found in tracked records.")

    return changed_files_count > total_files * 0.5  # Return True if more than 50% of files changed

if __name__ == '__main__':
    result = check_magic_numbers()
    if result:
        logger.debug("More than 50% of the files in the directory have changed file types.")
    else:
        logger.debug("Less than or equal to 50% of the files in the directory have changed file types.")
