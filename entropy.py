import os
import math
import time
from concurrent.futures import ThreadPoolExecutor
from logconfig import get_logger
import constants

logger = get_logger(__name__)

def makehist(data):
    wherechar = [-1] * 256
    hist = [0] * 256
    histlen = 0

    for char in data:
        index = char
        if wherechar[index] == -1:
            wherechar[index] = histlen
            histlen += 1
        hist[wherechar[index]] += 1

    return histlen, hist

def entropy(hist, histlen, length):
    H = 0
    for i in range(histlen):
        p = hist[i] / length
        if p > 0:  # avoid log2(0)
            H -= p * math.log2(p)
    return H

def calc_entropy_file(filename):
    try:
        with open(filename, 'rb') as fh:
            data = fh.read()
            histlen, hist = makehist(data)  # Pass the file content to makehist function
            H = entropy(hist, histlen, len(data))
            logger.debug(f"Entropy Value of {filename}: {H}")
            return H
    except Exception as e:
        logger.error(f"Error opening file {filename}: {e}")
        return -1

def calculate_entropy_for_files_in_directory(directories):
    try:
        start_time = time.time()
        files = []

        for directory in directories:
            file_count = 0
            for foldername, subfolders, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    file_size = os.path.getsize(file_path)

                    if file_size < constants.ENTROPY_FILE_SIZE_LIMIT * 1024:
                        file_count += 1
                        files.append(file_path)

                        if file_count >= constants.ENTROPY_FILE_COUNT_PER_DIRECTORY:
                            break
        
        logger.info("List of files:")
        for file_path in files:
            logger.info(file_path)

        total_files = 0  # Initialize the count for successfully processed files
        high_entropy_files = 0
        threshold_lower = 7.980
        threshold_upper = 8.000

        results = [calc_entropy_file(file) for file in files]

        for result in results:
            if result is not None:  # Check for files that were successfully processed
                total_files += 1
                if threshold_lower <= result <= threshold_upper:
                    high_entropy_files += 1

        elapsed_time = time.time() - start_time

        if total_files > 0:
            percentage_high_entropy = (high_entropy_files / total_files) * 100
            if percentage_high_entropy > 30:
                logger.info(f"Result: 1 - More than 30% of files have entropy within the specified range")
                return 1
            else:
                logger.info(f"Result: 0 - Less than or equal to 30% of files have entropy within the specified range")
                return 0
        else:
            logger.info("Result: 0 - No files found in the directory")

        logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")

    except Exception as e:
        logger.error(f"Error processing files in directory {directory}: {e}")

def main():
    user_directories = ["C:\\Users\\RWareUser\\Downloads", "C:\\Users\\RWareUser\\Documents", "C:\\Users\\RWareUser\\Desktop"]
    return calculate_entropy_for_files_in_directory(user_directories)

if __name__ == "__main__":
    main()