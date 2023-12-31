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
import inspect
import msvcrt
import code_integrity_check
from logconfig import get_logger
import crypto
import ssl

logger = get_logger(__name__)

tested_up = None
FAULTY = 1
CODE_INTEGRITY_CHECK_FLAG = False

def start_algo(faulty, connections, num_connections, node_num):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    global FAULTY
    global tested_up

    FAULTY = faulty
    tested_up = [-1] * constants.NUM_NODES

    # init cert
    private_key = crypto.gen_pri_key()
    csr = crypto.gen_CSR(private_key)
    communication.req_CSR(csr)

    # # Check if the './test' directory exists
    # test_directory = "./test"
    # if not os.path.exists(test_directory):
    #     logger.error(f"{current_function_name} - The '{test_directory}' directory does not exist.")
    #     return

    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creating socket
    server_fd.bind(('0.0.0.0', constants.PORT))
    server_fd.listen(10)

    # Start the thread
    threading.Thread(target=receive_thread, args=(server_fd,)).start()

    # # Build the initial lookup table
    # files = [f for f in os.listdir(test_directory) if os.path.isfile(os.path.join(test_directory, f))]
    # files = [f for f in files if f not in ['.', '..']]
    # file_count = len(files)

    # if file_count == 0:
    #     logger.warning(f"{current_function_name} - There are no files in the '{test_directory}' directory.")

    # logger.debug(f"File count in '{test_directory}' directory: {file_count}")

    # file_lookup = []
    # for file in files:
    #     temp_filename = os.path.join(test_directory, file)
    #     entrophy = entropy.calc_entropy_file(temp_filename)
    #     file_lookup.append({'filename': temp_filename, 'entropy': entrophy})

    # Wait for user input to begin testing
    ready = 0
    while not ready:
        ready = int(input("Enter 1 to begin testing other nodes: "))
    
    threading.Thread(target=adaptive_dsd, args=(faulty, connections, num_connections, node_num)).start()


def adaptive_dsd(faulty, connections, num_connections, node_num):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    code_integrity_status = False

    global FAULTY
    global tested_up

    FAULTY = faulty

    # print("\n*****At any point in time enter a new fault status (1 or 0) or 2 to diagnose:*****")
    start = time.time()

    while True:
        end = time.time()
        curr_time = end - start

        # Check for user input using select
        if msvcrt.kbhit():
            try:
                input_value = int(input())
            except Exception as e:
                logger.error(f"Input value is incorrect - {e}")
                continue

            if input_value in [0,1]:
                FAULTY = input_value
                logger.info(f"Fault status updated to {input_value}")
                
        if curr_time > constants.TESTING_INTERVAL and not FAULTY:
            logger.info(f"{current_function_name} - Starting the testing now after {constants.TESTING_INTERVAL} seconds. Tested up array - {tested_up}")
            update_arr(connections, num_connections, node_num)
                
            detection_status = monitor.run_detection()
            logger.info(f"{current_function_name} - Detection status - {detection_status}")
            
            # update cert after each round of detection
            private_key = crypto.gen_pri_key()  # Generate new private key
            csr = crypto.gen_CSR(private_key)  # Generate CSR using the private key
            communication.send_flag_to_CA(FAULTY)  # Report faulty status to CA
            communication.req_CSR(csr)  # Request cert from CA

            # update lookup table
            if not FAULTY and detection_status:
                FAULTY = 1
            
            #tested_up = [0,2,0]
            #node_num = 1
            logger.info(f"{current_function_name} - Starting diagnostics tested_up = {tested_up} and node_num = {node_num}")
            diagnosis = diagnose.diagnose(tested_up, node_num)
            logger.info(f"{current_function_name} - Diagnostics completed")
            for i in range(constants.NUM_NODES):
                if diagnosis[i] == 1:
                    logger.error(f"{current_function_name} - Node {i} is faulty")
                else:
                    logger.debug(f"{current_function_name} - Node {i} is not faulty")

            start = time.time()

def receive_thread(server_fd):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    try:
        while True:
            time.sleep(2)
            receiving(server_fd)
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error: {sock_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Error - {e}")
    finally:
        server_fd.close()

"""
Server side operation
receive msg_type and response
"""
def receiving(server_fd):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    current_sockets = [server_fd]
    ready_sockets = None
    k = 0

    global tested_up
    global FAULTY

    try:
        while True:
            k += 1
            try:
                ready_sockets, _, _ = select.select(current_sockets, [], [])
                logger.debug(f"{current_function_name} - Ready sockets read successfully")
            except Exception as e:
                logger.error(f"{current_function_name} - Error reading the ready sockets: {e}")
            
            for s in ready_sockets:
                if s == server_fd:
                    try:
                        client_socket, client_address = s.accept()
                        current_sockets.append(client_socket)
                        logger.debug(f"{current_function_name} - Client socket and address {client_address} details extracted sucessfully from a ready socket")
                    except Exception as e:
                        logger.error(f"{current_function_name} - Error extracting client details from ready socket - {e}")
                else:
                    msg_type, ssl_socket = communication.receive_msg(s)
                    if msg_type == constants.TEST_MSG:
                        try:
                            logger.info(f"{current_function_name} - Sending fault status - {FAULTY}")
                            communication.send_fault_status(ssl_socket, FAULTY)
                            logger.debug(f"{current_function_name} - Message Type - TEST_MSG - sent fault status successfully")
                        except Exception as e:
                            logger.error(f"{current_function_name} - Message Type - TEST_MSG - Error sending message - {e}")
                    elif msg_type == constants.REQUEST_MSG:
                        try:
                            communication.send_array(ssl_socket, tested_up)
                            logger.debug(f"{current_function_name} - Message Type - REQUEST_MSG - sent array successfully")
                        except Exception as e:
                            logger.error(f"{current_function_name} - Message Type - REQUEST_MSG - Error sending array - {e}")
                    elif msg_type == constants.CODE_INTEGRITY_MSG:
                        try:
                            communication.send_code_integrity_signature(ssl_socket)
                        except Exception as e:
                            logger.error(f"{current_function_name} - Message Type - CODE_INTEGRITY_MSG - Error sending data - {e}")
                    current_sockets.remove(s)
            if k == (len(current_sockets) * 2):
                break
    except socket.error as e:
        logger.error(f"Socket error: {e}")

def update_arr(connections, num_connections, node_num):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    global tested_up
    global CODE_INTEGRITY_CHECK_FLAG
    global FAULTY

    found_non_faulty = False
    for i in range(num_connections):
        try:

            if not CODE_INTEGRITY_CHECK_FLAG and constants.ENABLE_CODE_INTEGRITY_DETECTION:
                logger.debug(f"{current_function_name} - Initiating code integrity check")
                ssl_socket = communication.init_client_to_server(connections[i]['ip_addr'])
                if ssl_socket is None:
                    logger.error(f"SSL Socket not created to IP: {connections[i]['ip_addr']}")

                logger.debug(f"SSL Socket creation successful to IP: {connections[i]['ip_addr']}")
                code_integrity_status = communication.request_code_integrity_status(ssl_socket)
                CODE_INTEGRITY_CHECK_FLAG = True

                if not code_integrity_status:
                    FAULTY = 1

                try:
                    ssl_socket.close()
                except Exception as e:
                    logger.error(f"{current_function_name} - Failed to close SSL socket which is not alive")

            # Ask for fault status
            ssl_socket = communication.init_client_to_server(connections[i]['ip_addr'])
            if ssl_socket is None:
                logger.error(f"SSL Socket not created to IP: {connections[i]['ip_addr']}")
                continue
            
            logger.debug(f"SSL Socket creation successful to IP: {connections[i]['ip_addr']}")
            fault_status = communication.request_fault_status(ssl_socket)
            try:
                ssl_socket.close()
            except Exception as e:
                logger.error(f"{current_function_name} - Failed to close SSL socket which is not alive")

            if (not FAULTY and not fault_status) or (FAULTY and fault_status):  # TODO: Add more logic here
                ssl_socket = communication.init_client_to_server(connections[i]['ip_addr'])
                if ssl_socket is None:
                    logger.error(f"SSL Socket not created to IP: {connections[i]['ip_addr']}")
                    continue
                new_arr = communication.request_arr(ssl_socket)
                logger.info(f"{current_function_name} - New array value received from {connections[i]['ip_addr']}  - {new_arr}")
                try:
                    ssl_socket.close()
                except Exception as e:
                    logger.error(f"{current_function_name} - Failed to close socket which is not alive")

                ssl_socket = communication.init_client_to_server(connections[i]['ip_addr'])

                if ssl_socket is None:
                    logger.error(f"SSL Socket not created to IP: {connections[i]['ip_addr']}")
                    continue
                fault_status = communication.request_fault_status(ssl_socket)  # Check fault status again before updating array
                logger.info(f"{current_function_name} - received fault status from {connections[i]['ip_addr']}  - {fault_status}")
                try:
                    ssl_socket.close()
                except Exception as e:
                    logger.error(f"{current_function_name} - Failed to close socket which is not alive")
                
                if (not FAULTY and not fault_status) or (FAULTY and fault_status):
                    update_tested_up(new_arr, node_num, connections[i]['node_num'])
                    found_non_faulty = True
                    break
        
        except ssl.SSLError as ssl_err:
            logger.error(f"{current_function_name} - SSL error - {ssl_err}")
        except socket.error as e:
            logger.error(f"{current_function_name} - Socket error - {e}")
        
        finally:
            try:
                ssl_socket.close()
            except Exception as e:
                logger.error(f"{current_function_name} - Failed to close socket which is not alive")

    if not found_non_faulty:
        tested_up[node_num] = -1
        print("Every connected node is faulty")


def update_tested_up(new_arr, node, tested_node):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    global tested_up

    logger.debug(f"{current_function_name} - Before updation of tested_up - {tested_up}")

    tested_up[node] = tested_node

    for i in range(constants.NUM_NODES):
        if i != node:
            tested_up[i] = new_arr[i]

    logger.info(f"{current_function_name} - After updation of tested_up - {tested_up}")