import diagnose
import sys
import communication
import constants
from colorama import Fore, Style, init
from logconfig import get_logger
import argparse

logger = get_logger(__name__)

if sys.platform == "win32":
    import adaptive as adaptive
else: # darwin and Linux
    import adaptive_unix as adaptive

rSentinel_art = r"""
        _________              __  .__              .__   
_______/   _____/ ____   _____/  |_|__| ____   ____ |  |  
\_  __ \_____  \_/ __ \ /    \   __\  |/    \_/ __ \|  |  
 |  | \/        \  ___/|   |  \  | |  |   |  \  ___/|  |__
 |__| /_______  /\___  >___|  /__| |__|___|  /\___  >____/
              \/     \/     \/             \/     \/      
"""
tagline_art = r"""
  ___  _    _       _ _         _          _   ___                                             ___       __                 
 |   \(_)__| |_ _ _(_) |__ _  _| |_ ___ __| | | _ \__ _ _ _  ______ _ ____ __ ____ _ _ _ ___  |   \ ___ / _|___ _ _  __ ___ 
 | |) | (_-<  _| '_| | '_ \ || |  _/ -_) _` | |   / _` | ' \(_-< _ \ '  \ V  V / _` | '_/ -_) | |) / -_)  _/ -_) ' \/ _/ -_)
 |___/|_/__/\__|_| |_|_.__/\_,_|\__\___\__,_| |_|_\__,_|_||_/__|___/_|_|_\_/\_/\__,_|_| \___| |___/\___|_| \___|_||_\__\___|
                                                                                                                            
"""

tagline_art1 = "Distributed Ransomware Defence"

def main():
    print(Fore.GREEN + rSentinel_art + Fore.RESET)
    print(Fore.GREEN + tagline_art + Fore.RESET)
    logger.info(Fore.RESET + "Starting rSentinel - A distributed ransomware defence system")
    this_node = None
    fault_status = None

    parser = argparse.ArgumentParser(description='P2P Node Configuration')
    parser.add_argument('-n', '--this_node', type=int, required=True, help='Node number')
    parser.add_argument('-f', '--fault_status', type=int, required=True, help='Fault status (0 or 1)')

    args = parser.parse_args()

    this_node = args.this_node
    fault_status = args.fault_status

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

    adaptive.start_algo(fault_status, connections, num_connections, this_node)

if __name__ == "__main__":
    main()
