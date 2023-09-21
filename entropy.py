from math import log2
import logging
import inspect

logging.basicConfig(level=logging.INFO)

def makehist(fh, flen):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    wherechar = [-1] * 256
    hist = [0] * 256
    histlen = 0

    try:
        fh.seek(0)
        c = fh.read(102400)  # Read the file in 102400 byte chunks
        logging.info(f"File Size: {flen}")
    except Exception as e:
        logging.error(f"Error reading file: {e}")

    for char in c:
        # index = ord(char)
        index = char
        if wherechar[index] == -1:
            wherechar[index] = histlen
            histlen += 1
        hist[wherechar[index]] += 1

    return histlen, hist


def entropy(hist, histlen, len):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    H = 0
    for i in range(histlen):
        p = hist[i] / len
        if p > 0:  # avoid log2(0)
            H -= p * log2(p)
    return H

def calc_entropy_file(filename):
    logging.info("File currently being read: %s", filename)
    try:
        with open(filename, 'rb') as fh:
            data = fh.read()
            fsz = len(data)  # Get file size
            # logging.info(f"File Size of {filename}: {fsz}")
            histlen, hist = makehist(fh, fsz)  # Using the previously defined makehist function
            # logging.info(f"Histlen: {histlen}, Hist: {hist}")
            H = entropy(hist, histlen, fsz)  # Using the previously defined entropy function
            logging.info(f"Entropy Value of {filename}: {H}")
            return H
    except Exception as e:
        logging.error(f"Error opening file {filename}: {e}")
        return -1
