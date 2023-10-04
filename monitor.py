import constants
import entropy
import inspect
import logging

def run_detection(entropies):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    encrp_files = update_entropy(entropies)
    if encrp_files / len(entropies) > constants.ENTROPHY_INCREASE_BATCH:
        return 1
    else:
        return 0

def update_entropy(entropies):
    encrp_files = 0
    for curr in entropies:
        entr = entropy.calc_entropy_file(curr['filename'])
        if entr == -1:
            encrp_files += 1
        elif (entr - curr['entropy']) / curr['entropy'] > constants.ENTROPHY_INCREASE_FILE:
            encrp_files += 1
        curr['entropy'] = entr

    return encrp_files