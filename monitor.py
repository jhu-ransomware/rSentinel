import constants
import entropy
import inspect
import logging
import canary
import fuzzysd
import file_type_changes as ftc

logger = logging.getLogger(__name__)

def run_detection(entropies):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.debug(f"Currently executing: {current_function_name}")

    cnt = 0 # counter for check fail: entropy increasing or canary modification

    logging.debug(f"Currently executing: Entropy Check")
    encrp_files = update_entropy(entropies)
    if encrp_files / len(entropies) > constants.ENTROPHY_INCREASE_BATCH:
        cnt += 1

    logging.debug(f"Currently executing: Canary File Check")
    ori_digest = canary.createCanary()
    if canary.chkCanaryChange(canary.canary_file, ori_digest):
        cnt += 1
    
    logging.debug(f"Currently executing: File Type Changes")
    if ftc.check_magic_numbers():
        cnt += 1
    logging.debug(f"Currently executing: Fuzzy Hashing")
    # Assuming fuzzysd.directory_path is set appropriately before calling run_go_script

    result_fuzzy = fuzzysd.run_go_script()

    status, _ = result_fuzzy  # Extract the status from the tuple

    if not isinstance(status, int) or status not in [0, 1]:
        raise ValueError(f"Invalid status from fuzzysd: {status}. Expected 0 or 1.")
    
    if status == 1:
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
