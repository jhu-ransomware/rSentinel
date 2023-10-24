import constants
import entropy
import inspect
import logging
import canary

logger = logging.getLogger(__name__)

def run_detection(entropies):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.debug(f"Currently executing: {current_function_name}")

    cnt = 0 # counter for check fail

    logging.debug(f"Currently executing: entropy check.")
    encrp_files = update_entropy(entropies)
    if encrp_files / len(entropies) > constants.ENTROPHY_INCREASE_BATCH:
        #return 1 
        cnt += 0       
    #else:
        #return 0
    
    logging.debug(f"Currently executing: canary file check.")
    ori_digest = canary.createCanary()
    if canary.chkCanaryChange(canary.canary_file, ori_digest):
        cnt += 1

    if cnt > 0:
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