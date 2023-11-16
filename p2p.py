import diagnose
import sys
import communication
import constants
import logging
from colorama import Fore, Style, init

init()

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    RED = Fore.RED
    RESET = Style.RESET_ALL
    FORMAT = "%(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: RESET + FORMAT,
        logging.INFO: RESET + FORMAT,
        logging.WARNING: RESET + FORMAT,
        logging.ERROR: RED + FORMAT,
        logging.CRITICAL: RED + FORMAT
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logging.basicConfig(level=logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
ch.setFormatter(CustomFormatter())

if sys.platform == "win32":
    import adaptive as adaptive
else: # darwin and Linux
    import adaptive_unix as adaptive

def main():
    logger = logging.getLogger(__name__)
    logger.addHandler(ch)
    logger.propagate = False
    logger.debug("Starting the application")

    this_node = int(input("What's your node number:"))
    faulty = int(input("Enter your fault status:"))

    try:
        with open("connections.txt", "r") as file:
            num_connections = int(file.readline())
            nodes = []
            for line in file:
                node_num, ip_addr = line.strip().split()
                nodes.append({"node_num": int(node_num), "ip_addr": ip_addr})

    except FileNotFoundError:
        logger.error("Error opening connections file")
        exit(1)

    ptr = 0
    while ptr < num_connections and nodes[ptr]['node_num'] < this_node:
        ptr += 1
    if ptr == num_connections:
        ptr = 0

    connections = []
    for i in range(num_connections):
        connections.append(nodes[ptr])
        ptr = (ptr + 1) % num_connections

    # Debugging
    logger.debug(f"Connections ({num_connections}):")
    for conn in connections:
        logger.debug(f"ip_addr:{conn['ip_addr']} node_num:{conn['node_num']}")

    adaptive.start_algo(faulty, connections, num_connections, this_node)

if __name__ == "__main__":
    main()
