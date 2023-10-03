import socket
import threading
import os
import select
import time
import sys
import time
import threading
import constants
import entropy
import diagnose
import communication
import monitor
import logging
import inspect
import selectors

tested_up = None

def start_algo(faulty, connections, num_connections, node_num):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    global FAULTY
    global tested_up

    FAULTY = faulty
    tested_up = [-1] * constants.NUM_NODES

    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creating socket
    server_fd.bind(('0.0.0.0', constants.PORT))
    server_fd.listen(5)

    DEMO = int(input("Please enter if you wish to send results to a demo (1 for yes, 0 for no):\n"))

    # Start the thread
    threading.Thread(target=receive_thread, args=(server_fd,)).start()

    # Build the initial lookup table
    path = "./test"
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if f not in ['.', '..']]
    file_count = len(files)

    logging.info(f"File count in 'test' directory: {file_count}")
    

    file_lookup = []
    for file in files:
        temp_filename = os.path.join(path, file)
        entrophy = entropy.calc_entropy_file(temp_filename)
        file_lookup.append({'filename': temp_filename, 'entrophy': entrophy})

    # Wait for user input to begin testing
    ready = 0
    while not ready:
        ready = int(input("Enter 1 to begin testing other nodes:\n"))

    adaptive_dsd(faulty, connections, num_connections, node_num, file_lookup)

    server_fd.close()


def adaptive_dsd(faulty, connections, num_connections, node_num, lookup):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    global FAULTY
    global tested_up

    FAULTY = faulty

    print("\n*****At any point in time enter a new fault status (1 or 0) or 2 to diagnose:*****")
    start = time.time()

    selector = selectors.DefaultSelector()

    # Register sys.stdin for read events
    selector.register(sys.stdin, selectors.EVENT_READ)

    while True:
        end = time.time()
        curr_time = end - start

        # Check for user input using select
        for key, _ in selector.select(0):
            if key.fileobj is sys.stdin:
                input_value = int(input())
            
            # Commenting out below for now to not allow manual update of fault
            # if input_value in [0, 1]:
            #     FAULTY = input_value
            #     print(f"Fault status changed to {FAULTY}")

            if input_value == 2:
                diagnosis = diagnose.diagnose(tested_up, node_num)
                print("Diagnosis:")
                for i in range(constants.NUM_NODES):
                    if diagnosis[i] == 1:
                        print(f"Node {i} is faulty")
                    else:
                        print(f"Node {i} is not faulty")
            else:
                print("Invalid input. Enter 1 or 0 to change fault status, or 2 to diagnose.")
                
        if curr_time > constants.TESTING_INTERVAL:
            update_arr(connections, num_connections, node_num)
            if constants.DEMO:
                diagnosis = diagnose(constants.tested_up, node_num)
                communication.send_msg_to_demo_node(constants.DEMO_IP, node_num, diagnosis, constants.NUM_NODES)

            # update lookup table
            if not FAULTY and monitor.run_detection(lookup):
                FAULTY = 1

            start = time.time()

def receive_thread(server_fd):
    while True:
        time.sleep(2)
        receiving(server_fd)

def receiving(server_fd):
    address = ('', 0)  # Dummy initial value
    buffer_size = 2000
    current_sockets = [server_fd]
    k = 0

    while True:
        k += 1
        ready_sockets, _, _ = select.select(current_sockets, [], [])

        for s in ready_sockets:
            if s == server_fd:
                client_socket, client_address = s.accept()
                current_sockets.append(client_socket)
            else:
                msg_type = communication.receive_msg(s)
                if msg_type == "TEST_MSG":
                    communication.send_fault_status(s, FAULTY)
                elif msg_type == "REQUEST_MSG":
                    communication.send_array(s, constants.tested_up, constants.NUM_NODES)
                s.close()
                current_sockets.remove(s)

        if k == (len(current_sockets) * 2):
            break


def update_arr(connections, num_connections, node_num):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    found_non_faulty = False
    for i in range(num_connections):
        try:
            sock = communication.init_client_to_server(connections[i]['ip_addr'])
            if sock is None:
                print("Issue creating a socket")
                continue

            # Ask for fault status
            fault_status = communication.request_fault_status(sock)
            if (not FAULTY and not fault_status) or (FAULTY and fault_status):  # TODO: Add more logic here
                new_arr = [0] * constants.NUM_NODES
                communication.request_arr(sock, new_arr)
                fault_status = communication.request_fault_status(sock)  # Check fault status again before updating array
                
                if (not FAULTY and not fault_status) or (FAULTY and fault_status):
                    update_tested_up(new_arr, node_num, connections[i]['node_num'])
                    found_non_faulty = True
                    break

            sock.close()

        except socket.error as e:
            print(f"Socket error: {e}")

    if not found_non_faulty:
        constants.tested_up[node_num] = -1
        print("Every connected node is faulty")


def update_tested_up(new_arr, node, tested_node):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    constants.tested_up[node] = tested_node
    
    for i in range(constants.NUM_NODES):
        if i < constants.NUM_NODES - 1:
            print(constants.tested_up[i], end=' ')
        else:
            print(constants.tested_up[i])

    for i in range(constants.NUM_NODES):
        if i != node:
            constants.tested_up[i] = new_arr[i]

    for i in range(constants.NUM_NODES):
        if i < constants.NUM_NODES - 1:
            print(constants.tested_up[i], end=' ')
        else:
            print(constants.tested_up[i])