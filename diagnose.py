import constants
import inspect
from logconfig import get_logger

logger = get_logger(__name__)

def diagnose(tested_up, index):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    state_x = [1] * constants.NUM_NODES
    visited = set()
    visited_count = 0

    ptr = index
    while True:
        if ptr in visited:
            visited_count += 1
            if visited_count >= 5:
                break
        visited.add(ptr)
        state_x[ptr] = 0
        ptr = tested_up[ptr]
        if ptr == index or ptr == -1:
            break

    return state_x