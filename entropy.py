from math import log2

def makehist(fh, len):
    wherechar = [-1] * 256
    hist = [0] * 256
    histlen = 0

    c = fh.read(102400)  # Read the file in 102400 byte chunks

    for char in c:
        index = ord(char)
        if wherechar[index] == -1:
            wherechar[index] = histlen
            histlen += 1
        hist[wherechar[index]] += 1

    return histlen, hist


def entropy(hist, histlen, len):
    H = 0
    for i in range(histlen):
        p = hist[i] / len
        if p > 0:  # avoid log2(0)
            H -= p * log2(p)
    return H

def calc_entropy_file(filename):
    try:
        with open(filename, 'rb') as fh:
            data = fh.read()
            fsz = len(data)  # Get file size
            histlen, hist = makehist(data, fsz)  # Using the previously defined makehist function
            H = entropy(hist, histlen, fsz)  # Using the previously defined entropy function
            return H
    except Exception as e:
        print(f"Error opening file {filename}: {e}")
        return -1
