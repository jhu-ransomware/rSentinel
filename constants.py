# Constants
IP_LENGTH = 16
PORT = 10100
DEMO_PORT = 10200
TESTING_INTERVAL = 5
NUM_NODES = 3

TEST_MSG = 1
REQUEST_MSG = 2

ENTROPHY_INCREASE_FILE = 0.5
ENTROPHY_INCREASE_BATCH = 0.5

SOCKET_TIMEOUT_GLOBAL = 30

NON_FAULTY_VAL = "WE_ARE_GOOD"

# Structures

class Connection:
    def __init__(self):
        self.ip_addr = ""  # this will be a string of max length IP_LENGTH
        self.node_num = 0

class FileEntr:
    def __init__(self):
        self.filename = ""  # this will be a string of max length 100
        self.entrophy = 0.0