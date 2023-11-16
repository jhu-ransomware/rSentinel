import socket
import struct
import hashlib
import socket
import struct
import constants
import inspect
import code_integrity_check
from logconfig import get_logger

logger = get_logger(__name__)

def request_arr(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    req_msg_data = struct.pack('!I', constants.REQUEST_MSG)
    sock.send(req_msg_data)

    # buffer_data = sock.recv(constants.NUM_NODES * 4)
    buffer_data = sock.recv(1024)

    arr = [0] * constants.NUM_NODES
    try:
        arr = list(struct.unpack('!' + 'i'*constants.NUM_NODES, buffer_data))
        logger.debug(f"{current_function_name} - Received array - {arr}")
    except Exception as e:
        logger.error(f"{current_function_name} - Error unpacking received socket data - {e}")

    return arr


def send_msg_to_demo_node(node_num, arr):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

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
    logger.debug(f"Currently executing: {current_function_name}")

    buffer = [struct.pack('!i', val) for val in arr]  # Convert integers to network byte order
    buffer_bytes = b''.join(buffer)  # Join the byte arrays to create a single byte string
    try:
        sock.sendall(buffer_bytes)
    except socket.error as e:
        print("Error sending tested up:", e)


def hash_string(s):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 4294967296


def send_fault_status(sock, faulty):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    status = struct.pack('!I', hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)))  # Convert to network byte order

    if faulty:
        fault_val = "Lorem ipsum"
        status = struct.pack('!I', hash(fault_val, len(constants.NON_FAULTY_VAL)))

    try:
        sock.sendall(status)
    except socket.error as e:
        logger.error(f"{current_function_name} - Error sending tested up - {e}")
        # print("Error sending tested up:", e)


def receive_msg(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    msg_type_data = sock.recv(4)  # Assuming 4 bytes for an integer, as it is in C
    if len(msg_type_data) != 4:
        raise ConnectionError("Failed to receive all 4 bytes for the message type")
    # msg_type_data = sock.recv(1024)  # Assuming 4 bytes for an integer, as it is in C
    logger.debug(f"{current_function_name} - Message type: {msg_type_data}")
    msg_type = struct.unpack('!I', msg_type_data)[0]  # Unpacking the received data
    return msg_type


def init_client_to_server(ip_address):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
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
    logger.debug(f"Currently executing: {current_function_name}")
    # Dummy hash function for the sake of conversion. 
    # Replace this with your actual hash function.
    return sum(ord(c) for c in val) 


def init_demo_socket():

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(('127.0.0.1', constants.DEMO_PORT))
        return sock
    except socket.error as err:
        print("Socket creation/connection error:", err)
        return None

def request_fault_status(sock):

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    status_data = None
    status = None

    try:
        test_msg_data = struct.pack('!I', constants.TEST_MSG)  # Pack the TEST_MSG as a 4-byte integer
        sock.send(test_msg_data)
        logger.debug(f"Test message sent successfully")

        status_data = sock.recv(4)  # Assuming 4 bytes for an integer, as it is in C
        logger.debug(f"Length of the status data: {len(status_data)}")

        status = struct.unpack('!I', status_data)[0]  # Unpacking the received data
        logger.debug(f"Status data: {status}")
    except ConnectionError as e:
        logger.error(f"Failed to receive all 4 bytes for the status")
    except socket.timeout as e:
        logger.error(f"Socket connection timed out")
    except Exception as e:
        logger.error(f"Socket error: {e}")

    if status == hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)):
        return 0
    return 1

def request_code_integrity_signature(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    code_integrity_verified = False

    try:
        combined_hash = code_integrity_check.generate_combined_hash()
        test_msg_data = struct.pack('!I', constants.CODE_INTEGRITY_MSG)  # Pack the TEST_MSG as a 4-byte integer
        sock.send(test_msg_data)
        logger.debug(f"Code integrity message request sent successfully")

        signed_signature = sock.recv(1024)  # Assuming 4 bytes for an integer, as it is in C
        logger.critical(f"{current_function_name} - received signature - {signed_signature}")

        code_integrity_verified = code_integrity_check.verify_signature(combined_hash, signed_signature)
        
    except socket.timeout as e:
        logger.error(f"Socket connection timed out")
    except Exception as e:
        logger.error(f"Socket error: {e}")
    finally:
        return code_integrity_verified

def send_code_integrity_signature(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    try:
        combined_hash = code_integrity_check.generate_combined_hash()
        sock.sendall(combined_hash)
        logger.debug(f"Code integrity message sent successfully")
    except socket.timeout as e:
        logger.error(f"Socket connection timed out")
    except Exception as e:
        logger.error(f"Socket error: {e}")