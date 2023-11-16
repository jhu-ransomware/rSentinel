import logging
import inspect
import os
import hashlib

logger = logging.getLogger(__name__)
canary_file = "CanaryFile"
canary_file_size = 1024

"""
Create Canary file
"""
def createCanary():
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    # remove old canary file
    if os.path.exists(canary_file):
        os.remove(canary_file)
        logger.debug("Previous canary file deleted.")
    else:
        logger.debug("No previous canary file on this node.")

    # generate canary file
    with open(canary_file, "wb") as c_f:
        c_f.write(os.urandom(canary_file_size))


    # hashdigest of canary file
    canary_digest = hashlib.md5(open(canary_file, "rb").read()).hexdigest()
    logger.debug(f"Canary file generated.\n Hash digest:{canary_digest}")
    return canary_digest

"""
Check Canary file
True: faulty
False: not faulty
"""
def chkCanaryChange(canary_file: str, ori_digest) -> bool:
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    if os.path.exists(canary_file):
        current_digest = hashlib.md5(open(canary_file, "rb").read()).hexdigest()
        if current_digest == ori_digest:
            logger.debug("Canary file has not been changed.")
            return False
        else:
            logger.debug("Canary file has been changed!")
            return True
    else:
        logger.error("Canary file doesn't exist!")
        return False
