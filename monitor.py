import constants
import entropy
import inspect
import logging

def run_detection(entrophies):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

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