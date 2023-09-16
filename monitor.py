import constants
import entropy

def run_detection(entrophies):
    encrp_files = update_entropy(entrophies)
    if encrp_files / len(entrophies) > constants.ENTROPHY_INCREASE_BATCH:
        return 1
    else:
        return 0

def update_entropy(entrophies):
    encrp_files = 0
    for curr in entrophies:
        entr = entropy.calc_entropy_file(curr['filename'])
        if entr == -1:
            encrp_files += 1
        elif (entr - curr['entropy']) / curr['entropy'] > constants.ENTROPHY_INCREASE_FILE:
            encrp_files += 1
        curr['entropy'] = entr

    return encrp_files