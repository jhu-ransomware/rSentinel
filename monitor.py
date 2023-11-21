import entropy
import inspect
import canary
import fuzzysd
import file_type_changes as ftc
from logconfig import get_logger

logger = get_logger(__name__)

def run_detection():
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    cnt = 0  # counter for check fail: entropy increasing or canary modification

    logger.info(f"Currently executing: Entropy Check")
    result_entropy = entropy.main()
    if result_entropy:
        cnt += 1
    
    logger.info(f"Count value after entropy: {cnt}")

    # logger.debug(f"Currently executing: File Type Changes")
    # if ftc.check_magic_numbers():
    #     cnt += 1

    logger.info(f"Currently executing: Canary File Check")
    result_canary = canary.execute_canary_logic()
    if result_canary:
        cnt += 1
    logger.info(f"Count value after canary: {cnt}")

    logger.info(f"Currently executing: Fuzzy Hashing")
    result_fuzzy = fuzzysd.run_go_script()
    status, _ = result_fuzzy  # Extract the status from the tuple
    logger.info(f'The status is {status}')
    if not isinstance(status, int) or status not in [0, 1]:
        raise ValueError(f"Invalid status from fuzzysd: {status}. Expected 0 or 1.")
    if status == 1:
        cnt += 1
    logger.info(f"Count value after fuzzy: {cnt}")

    logger.info(f"Count value after all checks: {cnt}")
    if cnt > 0:
        logger.error(f"{current_function_name} = Node is faulty")
        return 1
    else:
        return 0

