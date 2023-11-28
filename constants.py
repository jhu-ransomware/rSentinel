# Constants
IP_LENGTH = 16
PORT = 10100
DEMO_PORT = 10200
TESTING_INTERVAL = 60
NUM_NODES = 3

TEST_MSG = 1
REQUEST_MSG = 2
CODE_INTEGRITY_MSG = 3

ENTROPHY_INCREASE_FILE = 0.5
ENTROPHY_INCREASE_BATCH = 0.5

SOCKET_TIMEOUT_GLOBAL = 250

NON_FAULTY_VAL = "WE_ARE_GOOD"

TEST_DIR = "./test/"

CODE_DIR = "./"

COMBINED_HASH_VARIABLE = "RSENTINEL_COMBINED_HASH"
ENV_VAR_DEFAULT_VALUE = "Hello World"


"""
This variable sets the maximum file size limit (in KB) for scanning file entropies.
Files larger than this limit will be excluded from entropy calculations.
Setting this limit helps to reduce computation time and improve system performance.
For example, to set a limit of 500KB, the value of this variable should be 500.
"""
ENTROPY_FILE_SIZE_LIMIT = 500


"""
This variable defines the limit on the number of files to be scanned for entropy in each directory.
The code will select a sample of files up to this limit from each directory to perform entropy analysis.
Setting this limit helps in managing the analysis workload and improves performance by focusing on a subset of files.
For example, a value of 2 means only two files from each directory will be chosen for entropy scanning.
"""
ENTROPY_FILE_COUNT_PER_DIRECTORY = 2



# Structures

class Connection:
    def __init__(self):
        self.ip_addr = ""  # this will be a string of max length IP_LENGTH
        self.node_num = 0

class FileEntr:
    def __init__(self):
        self.filename = ""  # this will be a string of max length 100
        self.entrophy = 0.0
