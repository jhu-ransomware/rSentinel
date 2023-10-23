import diagnose
import sys
import communication
import constants
import logging

logging.basicConfig(level=logging.DEBUG)

if sys.platform == "darwin":
    import adaptive_mac as adaptive
elif sys.platform == "win32":
    import adaptive as adaptive

def main():
    logger = logging.getLogger(__name__)
    logging.debug("Starting the application")

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
        print("Error opening connections file")
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
    print(f"Connections ({num_connections}):")
    for conn in connections:
        print(f"ip_addr:{conn['ip_addr']} node_num:{conn['node_num']}")

    adaptive.start_algo(faulty, connections, num_connections, this_node)

if __name__ == "__main__":
    main()