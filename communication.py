import socket
import struct
import hashlib
import socket
import struct
import constants
import inspect
import logging

def request_arr(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    req_msg_data = struct.pack('!I', constants.REQUEST_MSG)
    sock.send(req_msg_data)

    buffer_data = sock.recv(constants.NUM_NODES * 4)  # Assuming 4 bytes for an integer, as in C

    arr = []
    for i in range(constants.NUM_NODES):
        val = struct.unpack('!I', buffer_data[i*4:i*4+4])[0]
        arr.append(val)

    return arr

def send_msg_to_demo_node(node_num, arr):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    sock = init_demo_socket()
    if sock is None:
        print("Issue creating a socket")
        return

    buffer_size = len(arr)
    buffer_data = b''.join(struct.pack('!I', x) for x in arr)

    print(f"buffer size: {buffer_size}")
    for i in range(buffer_size):
        print(struct.unpack('!I', buffer_data[i*4:i*4+4])[0])

    try:
        sock.send(buffer_data)
    except socket.error as e:
        print(f"Error sending demo array: {e}")

    sock.close()


def send_array(sock, arr):

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    buffer = [struct.pack('!I', val) for val in arr]  # Convert integers to network byte order
    buffer_bytes = b''.join(buffer)  # Join the byte arrays to create a single byte string
    try:
        sock.sendall(buffer_bytes)
    except socket.error as e:
        print("Error sending tested up:", e)

def hash_string(s):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

def send_fault_status(sock, faulty):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    
    status = struct.pack('!I', hash_string(constants.NON_FAULTY_VAL))  # Convert to network byte order

    if faulty:
        fault_val = "Lorem ipsum"
        status = struct.pack('!I', hash_string(fault_val))

    try:
        sock.sendall(status)
    except socket.error as e:
        logging.error(f"{current_function_name} - Error sending tested up - {e}")
        # print("Error sending tested up:", e)

def receive_msg(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    msg_type_data = sock.recv(4)  # Assuming 4 bytes for an integer, as it is in C
    if len(msg_type_data) != 4:
        raise ConnectionError("Failed to receive all 4 bytes for the message type")
    msg_type = struct.unpack('!I', msg_type_data)[0]  # Unpacking the received data
    return msg_type

def init_client_to_server(ip_address):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(constants.SOCKET_TIMEOUT_GLOBAL)

    try:
        sock.connect((ip_address, constants.PORT))
        return sock
    except socket.error as err:
        print("Socket creation/connection error:", err)
        return None

def hash(val, length):  # You will need to define a hash function in Python or use an existing one like hashlib
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")
    # Dummy hash function for the sake of conversion. 
    # Replace this with your actual hash function.
    return sum(ord(c) for c in val) 


def init_demo_socket():

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(('127.0.0.1', constants.DEMO_PORT))
        return sock
    except socket.error as err:
        print("Socket creation/connection error:", err)
        return None

def request_fault_status(sock):

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logging.info(f"Currently executing: {current_function_name}")

    status = None

    try:
        test_msg_data = struct.pack('!I', constants.TEST_MSG)  # Pack the TEST_MSG as a 4-byte integer
        sock.send(test_msg_data)
        logging.info(f"Test message sent successfully")

        status_data = sock.recv(4)  # Assuming 4 bytes for an integer, as it is in C
        logging.info(f"Length of the status data: {len(status_data)}")

        if len(status_data) != 4:
            status = struct.unpack('!I', status_data)[0]  # Unpacking the received data
            logging.info(f"Status data: {status}")
            raise ConnectionError("Failed to receive all 4 bytes for the status")
    except ConnectionError as e:
        logging.error(f"Failed to receive all 4 bytes for the status")
    except socket.timeout as e:
        logging.error(f"Socket connection timed out")
    except Exception as e:
        logging.error(f"Socket error: {e}")

    if status == hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)):
        return 0
    return 1
