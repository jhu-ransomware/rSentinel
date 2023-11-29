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

logger = get_logger(__name__)

pri_key = 'pri.key'
crt_name = 'node.crt'
hostname = 'node1.c0conut.com'

"""
send the CSR to CA
"""
def req_CSR(CA_addr, CA_port, csr):
    if csr != None:
        # Send the CSR to the Baby CA
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((CA_addr, CA_port))
            print("Sending CSR...")
            sock.sendall(csr.public_bytes(serialization.Encoding.PEM))
            print("CSR sent!")
        
            # Receive data from the server and shut down
            received = sock.recv(2048)
            if len(received) > 20: # fail: 15

                if os.path.exists(crt_name):
                    os.remove(crt_name)

                with open(crt_name, 'wb') as f:
                    f.write(received)

                print(f"Certificate saved as {crt_name}")  
            else:
                print("Din't receive Certificate from Baby CA!")

"""
Send flag value to CA if node is faulty
Arg: 
    CA_addr
    CA port
    faulty (bool)
"""
def send_flag_to_CA(CA_addr, CA_flag_port, faulty):
    # only send if node is in faulty status
    if faulty:
        print("Node in faulty status. Report to CA.")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CA_addr, CA_flag_port))
            sock.send(b'1\n')

"""
Sends message with SSL socket. Client-side operation.
Arg: 
    sock (socket.socket)
    msg (bytes)
    ca_pem_path (str): Path to the CA PEM file
"""
def send_msg_SSL(sock, msg, ca_pem_path):
    logger.debug(f"Sending message via SSL: {msg}")

    context = ssl.create_default_context()
    context.load_verify_locations(ca_pem_path)

    try:
        with context.wrap_socket(sock, server_hostname=hostname) as ssl_sock:
            ssl_sock.sendall(msg)
    except ssl.SSLError as ssl_err:
        logger.error(f"SSL error while sending message: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"Socket error while sending message: {sock_err}")

"""
Verifies an SSL communication on the receiving end against a CA-issued certificate.
Arg:
    sock (socket.socket)
    cert (str): Path to the certificate file
    prikey (str): Path to the private key file
Ret: (bytes) or None
"""
def verify_recv(sock, cert, prikey):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert, keyfile=prikey)

    try:
        with context.wrap_socket(sock, server_side=True) as ssl_sock:
            received = ssl_sock.recv(1024)
            return received
    except ssl.SSLError as ssl_err:
        logger.error(f"SSL verification failed. SSL error: {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"Socket error in verify_recv: {sock_err}")
    except Exception as e:
        logger.error(f"General error in verify_recv: {e}")
    return None

"""
Sends a request message and receives an array
Arg:
    sock (socket.socket)
    cert (str)
    prikey (str)
    ca_pem_path (str)
Ret: (list)
"""
def request_arr(sock, cert, prikey, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    req_msg_data = struct.pack('!I', constants.REQUEST_MSG)
    send_msg_SSL(sock, req_msg_data, ca_pem_path)

    try:
        buffer_data = verify_recv(sock, cert, prikey)
        if buffer_data and len(buffer_data) == constants.NUM_NODES * 4:
            arr = list(struct.unpack('!' + 'i' * constants.NUM_NODES, buffer_data))
            logger.debug(f"{current_function_name} - Received array - {arr}")
            return arr
        else:
            logger.error(f"{current_function_name} - Incorrect data length received or no data.")
            return []
    except struct.error as e:
        logger.error(f"{current_function_name} - Error unpacking received socket data - {e}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error - {e}")
        return []


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


"""
Sends an array of integers over an SSL-secured socket connection.
Arg:
    sock (socket.socket)
    arr (list of int)
    ca_pem_path (str)
"""
def send_array(sock, arr, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        # Convert the array to bytes in network byte order
        buffer_bytes = b''.join(struct.pack('!i', val) for val in arr)
        send_msg_SSL(sock, buffer_bytes, ca_pem_path)
        logger.debug(f"Array sent successfully: {arr}")
    except struct.error as e:
        logger.error(f"{current_function_name} - Error in packing array data - {e}")
    except socket.error as e:
        logger.error(f"{current_function_name} - Socket error while sending array - {e}")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while sending array - {ssl_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error while sending array - {e}")

def hash_string(s):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 4294967296

"""
Sends a fault status over an SSL-secured socket connection.
Arg:
    sock (socket.socket)
    faulty (bool)
    ca_pem_path (str)
"""
def send_fault_status(sock, faulty, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        fault_val = "Lorem ipsum" if faulty else constants.NON_FAULTY_VAL
        status = struct.pack('!I', hash(fault_val, len(fault_val)))

        send_msg_SSL(sock, status, ca_pem_path)
        logger.debug(f"Fault status sent successfully: {'Faulty' if faulty else 'Non-faulty'}")
    except struct.error as e:
        logger.error(f"{current_function_name} - Error in packing fault status - {e}")
    except socket.error as e:
        logger.error(f"{current_function_name} - Socket error while sending fault status - {e}")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while sending fault status - {ssl_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error while sending fault status - {e}")

"""
Receives and unpacks a message over an SSL-secured socket connection.
Arg:
    sock (socket.socket)
    cert (str)
    prikey (str)
Ret: the unpacked message type (int)
    or None, if an error occurred
"""
def receive_msg(sock, cert, prikey):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        msg_type_data = verify_recv(sock, cert, prikey)
        if not msg_type_data or len(msg_type_data) != 4:
            raise ValueError("Incorrect message length received")

        msg_type = struct.unpack('!I', msg_type_data)[0]
        logger.debug(f"{current_function_name} - Message type received: {msg_type}")
        return msg_type
    except struct.error as e:
        logger.error(f"{current_function_name} - Error unpacking received data - {e}")
    except ValueError as e:
        logger.error(f"{current_function_name} - {e}")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error in receive_msg - {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error in receive_msg - {sock_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error in receive_msg - {e}")
        return None

"""
Initializes a client socket and connects it to the server.
Arg:
    ip_address (str)
Ret: the initialized socket (socket.socket) 
    or None, if failed
"""
def init_client_to_server(ip_address):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(constants.SOCKET_TIMEOUT_GLOBAL)
        sock.connect((ip_address, constants.PORT))
        logger.debug(f"Socket successfully connected to {ip_address}:{constants.PORT}")
        return sock
    except socket.error as err:
        logger.error(f"{current_function_name} - Socket creation/connection error: {err}")
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

"""
Sends a test message and receives a fault status response from the server.
Arg:
    sock (socket.socket)
    cert (str)
    prikey (str)
    ca_pem_path (str)
Ret: The fault status (int)
    0 for non-faulty, 1 for faulty
    None on error
"""
def request_fault_status(sock, cert, prikey, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        test_msg_data = struct.pack('!I', constants.TEST_MSG)
        send_msg_SSL(sock, test_msg_data, ca_pem_path)
        logger.debug("Test message sent successfully")

        status_data = verify_recv(sock, cert, prikey)
        if not status_data or len(status_data) != 4:
            raise ValueError("Incorrect length of status data received")

        status = struct.unpack('!I', status_data)[0]
        logger.debug(f"Status received: {status}")
        return 0 if status == hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)) else 1

    except struct.error as e:
        logger.error(f"{current_function_name} - Error unpacking received data - {e}")
    except ValueError as e:
        logger.error(f"{current_function_name} - {e}")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error - {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error - {sock_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error - {e}")
        return None

"""
Sends code integrity status and receives a response to verify a signature.
Arg:
    sock (socket.socket)
    cert (str)
    prikey (str)
    ca_pem_path (str)
Ret: (bool)
    True if the code integrity is verified, False otherwise.
"""
def request_code_integrity_status(sock, cert, prikey, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        combined_hash = code_integrity_check.generate_combined_hash()
        logger.info(f"{current_function_name} - Generated combined hash: {combined_hash}")

        test_msg_data = struct.pack('!I', constants.CODE_INTEGRITY_MSG)
        send_msg_SSL(sock, test_msg_data, ca_pem_path)
        logger.debug("Code integrity message request sent successfully")

        signed_signature = verify_recv(sock, cert, prikey)
        if not signed_signature:
            raise ValueError("No signature received for code integrity verification")

        return code_integrity_check.verify_signature(combined_hash, signed_signature)

    except struct.error as e:
        logger.error(f"{current_function_name} - Error packing/unpacking data - {e}")
    except ValueError as e:
        logger.error(f"{current_function_name} - {e}")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error - {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error - {sock_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error - {e}")
        return False

"""
Sends a hash signature for code integrity check
Arg:
    sock (socket.socket)
    ca_pem_path (str)
"""
def send_code_integrity_signature(sock, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    try:
        combined_hash = os.getenv(constants.COMBINED_HASH_VARIABLE, constants.ENV_VAR_DEFAULT_VALUE)
        logger.info(f"{current_function_name} - Retrieved combined hash: {combined_hash}")

        signed_hash = code_integrity_check.sign_data(combined_hash)
        if not signed_hash:
            raise ValueError("Failed to sign the hash for code integrity")

        send_msg_SSL(sock, signed_hash, ca_pem_path)
        logger.debug("Code integrity signature sent successfully")

    except ValueError as e:
        logger.error(f"{current_function_name} - {e}")
    except ssl.SSLError as ssl_err:
        logger.error(f"{current_function_name} - SSL error while sending code integrity signature - {ssl_err}")
    except socket.error as sock_err:
        logger.error(f"{current_function_name} - Socket error while sending code integrity signature - {sock_err}")
    except Exception as e:
        logger.error(f"{current_function_name} - Unexpected error while sending code integrity signature - {e}")

def send_code_integrity_signature(sock, ca_pem_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    try:
        combined_hash = os.getenv(constants.COMBINED_HASH_VARIABLE, constants.ENV_VAR_DEFAULT_VALUE)
        logger.info(f"{current_function_name} - Stored combined hash - {combined_hash}")
        signed_hash = code_integrity_check.sign_data(combined_hash)
        send_msg_SSL(sock, signed_hash, ca_pem_path)
        logger.debug(f"Code integrity message sent successfully")
    except socket.timeout as e:
        logger.error(f"Socket connection timed out")
    except Exception as e:
        logger.error(f"Socket error: {e}")