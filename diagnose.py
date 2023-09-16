import constants

def diagnose(tested_up, index):
    state_x = [1] * constants.NUM_NODES

    ptr = index
    while ptr != index and ptr != -1:
        state_x[ptr] = 0
        ptr = tested_up[ptr]

    return state_x