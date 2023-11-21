from math import log2
import inspect
from logconfig import get_logger

logger = get_logger(__name__)

def makehist(fh, flen):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    wherechar = [-1] * 256
    hist = [0] * 256
    histlen = 0

    try:
        fh.seek(0)
        c = fh.read(102400)  # Read the file in 102400 byte chunks
        logger.debug(f"File Size: {flen}")
    except Exception as e:
        logger.error(f"Error reading file: {e}")

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
    logger.debug(f"Currently executing: {current_function_name}")
    H = 0
    for i in range(histlen):
        p = hist[i] / len
        if p > 0:  # avoid log2(0)
            H -= p * log2(p)
    return H

def calc_entropy_file(filename):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    logger.debug("File currently being read: %s", filename)
    try:
        with open(filename, 'rb') as fh:
            data = fh.read()
            fsz = len(data)  # Get file size
            # logger.debug(f"File Size of {filename}: {fsz}")
            histlen, hist = makehist(fh, fsz)  # Using the previously defined makehist function
            # logger.debug(f"Histlen: {histlen}, Hist: {hist}")
            H = entropy(hist, histlen, fsz)  # Using the previously defined entropy function
            logger.debug(f"Entropy Value of {filename}: {H}")
            return H
    except Exception as e:
        logger.error(f"Error opening file {filename}: {e}")
        return -1
