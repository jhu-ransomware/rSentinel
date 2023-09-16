import socket
import struct
import hashlib
import socket
import struct
import constants

def request_arr(sock):
    req_msg_data = struct.pack('!I', constants.REQUEST_MSG)
    sock.send(req_msg_data)

    buffer_data = sock.recv(constants.NUM_NODES * 4)  # Assuming 4 bytes for an integer, as in C

    arr = []
    for i in range(constants.NUM_NODES):
        val = struct.unpack('!I', buffer_data[i*4:i*4+4])[0]
        arr.append(val)

    return arr

def send_msg_to_demo_node(node_num, arr):
    sock = init_demo_socket()  # Assumes you have defined this function earlier
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
    buffer = [struct.pack('!I', val) for val in arr]  # Convert integers to network byte order
    buffer_bytes = b''.join(buffer)  # Join the byte arrays to create a single byte string
    try:
        sock.sendall(buffer_bytes)
    except socket.error as e:
        print("Error sending tested up:", e)

def hash_string(s):
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

def send_fault_status(sock, faulty):
    NON_FAULTY_VAL = "NON_FAULTY_VAL"  # This should be defined elsewhere in your Python code
    
    status = struct.pack('!I', hash_string(NON_FAULTY_VAL))  # Convert to network byte order

    if faulty:
        fault_val = "Lorem ipsum"
        status = struct.pack('!I', hash_string(fault_val))

    try:
        sock.sendall(status)
    except socket.error as e:
        print("Error sending tested up:", e)

def receive_msg(sock):
    msg_type_data = sock.recv(4)  # Assuming 4 bytes for an integer, as it is in C
    if len(msg_type_data) != 4:
        raise ConnectionError("Failed to receive all 4 bytes for the message type")
    msg_type = struct.unpack('!I', msg_type_data)[0]  # Unpacking the received data
    return msg_type

def init_client_to_server(ip_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PORT = 8080  # Define your port number here

    try:
        sock.connect((ip_address, PORT))
        return sock
    except socket.error as err:
        print("Socket creation/connection error:", err)
        return None

def hash(val, length):  # You will need to define a hash function in Python or use an existing one like hashlib
    # Dummy hash function for the sake of conversion. 
    # Replace this with your actual hash function.
    return sum(ord(c) for c in val) 


def init_demo_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(('127.0.0.1', constants.DEMO_PORT))
        return sock
    except socket.error as err:
        print("Socket creation/connection error:", err)
        return None

def request_fault_status(sock):
    test_msg_data = struct.pack('!I', constants.TEST_MSG)  # Pack the TEST_MSG as a 4-byte integer
    sock.send(test_msg_data)

    status_data = sock.recv(4)  # Assuming 4 bytes for an integer, as it is in C
    if len(status_data) != 4:
        raise ConnectionError("Failed to receive all 4 bytes for the status")
    status = struct.unpack('!I', status_data)[0]  # Unpacking the received data

    if status == hash(constants.NON_FAULTY_VAL, len(constants.NON_FAULTY_VAL)):
        return 0
    return 1
