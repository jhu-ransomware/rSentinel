import constants
import inspect
import logging

def diagnose(tested_up, index):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    state_x = [1] * constants.NUM_NODES

    ptr = index
    while ptr != index and ptr != -1:
        state_x[ptr] = 0
        ptr = tested_up[ptr]

    return state_x