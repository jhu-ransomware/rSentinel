import socket
import struct
import hashlib
import socket
import struct
import constants
import inspect
import code_integrity_check
import os
from logconfig import get_logger
from cryptography.hazmat.primitives import serialization
import ssl
import crypto

logger = get_logger(__name__)

"""
send the CSR to CA
"""
def req_CSR(csr):
    if csr != None:
        # Send the CSR to the Baby CA
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((constants.CA_addr, constants.CA_port))
            print("Sending CSR...")
            sock.sendall(csr.public_bytes(serialization.Encoding.PEM))
            print("CSR sent!")
        
            # Receive data from the server and shut down
            received = sock.recv(2048)
            if len(received) > 20: # fail: 15

                if os.path.exists(constants.crt_name):
                    os.remove(constants.crt_name)

                with open(constants.crt_name, 'wb') as f:
                    f.write(received)

                print(f"Certificate saved as {constants.crt_name}") 
                #crypto.print_cert_info(constants.crt_name)
            else:
                print("Din't receive Certificate from Baby CA!")
"""
Send flag value to CA if node is faulty
Arg: 
    faulty (bool)
"""
def send_flag_to_CA(faulty):
    # only send if node is in faulty status
    if faulty:
        print("Node in faulty status. Report to CA.")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((constants.CA_addr, constants.CA_flag_port))
            sock.send(b'1\n')

"""
hash
"""
def hash_string(s):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 4294967296

def hash(val, length):  # You will need to define a hash function in Python or use an existing one like hashlib
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    # Dummy hash function for the sake of conversion. 
    # Replace this with your actual hash function.
    return sum(ord(c) for c in val) 

"""
receiving()
server-side operation
receive msg_type
"""
def receive_msg(sock):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=constants.crt_name, keyfile=constants.pri_key)
    ssl_socket = context.wrap_socket(sock, server_side=True)

    msg_type_data = ssl_socket.recv(4)  # Assuming 4 bytes for an integer, as it is in C
    logger.debug(f"msg_type_data: {msg_type_data}")
    if len(msg_type_data) != 4:
        raise ConnectionError("Failed to receive all 4 bytes for the message type")
    logger.debug(f"{current_function_name} - Message type: {msg_type_data}")
    msg_type = struct.unpack('!I', msg_type_data)[0]  # Unpacking the received data
    return msg_type, ssl_socket

"""
receiving() -> receive_msg()
server-side operation
response fault status, when receiving TEST_MSG
"""
def send_fault_status(ssl_socket, faulty):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    status = struct.pack('!I', hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)))  # Convert to network byte order

    if faulty:
        fault_val = "Lorem ipsum"
        status = struct.pack('!I', hash(fault_val, len(constants.NON_FAULTY_VAL)))

    try:
        ssl_socket.sendall(status)
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while sending message: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error while sending message: {sock_err}")

"""
receiving() -> receive_msg()
server-side operation
response array, when receiving REQUEST_MSG
"""
def send_array(ssl_socket, arr):

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    buffer = [struct.pack('!i', val) for val in arr]  # Convert integers to network byte order
    buffer_bytes = b''.join(buffer)  # Join the byte arrays to create a single byte string
    try:
        ssl_socket.sendall(buffer_bytes)
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while sending message: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error while sending message: {sock_err}")

"""
receiving() -> receive_msg()
server-side operation
response signed hash, when receiving CODE_INTEGRITY_MSG
"""
def send_code_integrity_signature(ssl_socket):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    try:
        combined_hash = os.getenv(constants.COMBINED_HASH_VARIABLE, constants.ENV_VAR_DEFAULT_VALUE)
        logger.info(f"{current_function_name} - Stored combined hash - {combined_hash}")
        signed_hash = code_integrity_check.sign_data(combined_hash)
        ssl_socket.sendall(signed_hash)
        logger.debug(f"Code integrity message sent successfully")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while sending message: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error while sending message: {sock_err}")

"""
init client-side SSL socket
"""
def init_client_to_server(ip_address):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(constants.SOCKET_TIMEOUT_GLOBAL)

    context = ssl.create_default_context()
    context.load_verify_locations(constants.ca_pem_path)
    ssl_socket = context.wrap_socket(sock, server_hostname=ip_address)

    try:
        ssl_socket.connect((ip_address, constants.PORT))
        return ssl_socket
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while initializing SSL socket: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error while initializing SSL socket: {sock_err}")
    return None

"""
update_arr()
clinet-side operation
request code integrity status when SSL socket is created
"""
def request_code_integrity_status(ssl_socket):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    code_integrity_verified = False

    try:
        combined_hash = code_integrity_check.generate_combined_hash()
        logger.info(f"{current_function_name} - Generated combined hash - {combined_hash}")
        test_msg_data = struct.pack('!I', constants.CODE_INTEGRITY_MSG)  # Pack the TEST_MSG as a 4-byte integer
        ssl_socket.sendall(test_msg_data)
        logger.debug(f"Code integrity message request sent successfully")

        signed_signature = ssl_socket.recv(1024)  # Assuming 4 bytes for an integer, as it is in C

        code_integrity_verified = code_integrity_check.verify_signature(combined_hash, signed_signature)
        
    except socket.timeout as e:
        logger.error(f"{current_function_name} - Socket connection timed out")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error when requesting code integrity status: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error when requesting code integrity status: {sock_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - {e}")
    finally:
        return code_integrity_verified

"""
update_arr()
clinet-side operation
request fault status when SSL socket is created
"""
def request_fault_status(ssl_socket):

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    status_data = None
    status = None

    try:
        test_msg_data = struct.pack('!I', constants.TEST_MSG)  # Pack the TEST_MSG as a 4-byte integer
        ssl_socket.send(test_msg_data)
        logger.debug(f"Test message sent successfully")

        status_data = ssl_socket.recv(4)  # Assuming 4 bytes for an integer, as it is in C
        logger.debug(f"status_data: {status_data}")
        logger.debug(f"Length of the status data: {len(status_data)}")

        status = struct.unpack('!I', status_data)[0]  # Unpacking the received data
        logger.debug(f"Status data: {status}")
    except ConnectionError as e:
        logger.error(f"Failed to receive all 4 bytes for the status")
    except socket.timeout as e:
        logger.error(f"Socket connection timed out")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error when requesting code integrity status: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error when requesting code integrity status: {sock_err}")
    except Exception as e:
        logger.error(f"Socket error: {e}")

    if status == hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)):
        return 0
    return 1

"""
update_arr()
clinet-side operation
request arr when SSL socket is created
"""
def request_arr(ssl_socket):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    req_msg_data = struct.pack('!I', constants.REQUEST_MSG)
    ssl_socket.send(req_msg_data)

    # buffer_data = sock.recv(constants.NUM_NODES * 4)
    buffer_data = ssl_socket.recv(1024)
    logger.debug(f"buffer_data: {buffer_data}")
    arr = [0] * constants.NUM_NODES
    try:
        arr = list(struct.unpack('!' + 'i'*constants.NUM_NODES, buffer_data))
        logger.debug(f"{current_function_name} - Received array - {arr}")
    except Exception as e:
        logger.error(f"{current_function_name} - Error unpacking received socket data - {e}")

    return arr