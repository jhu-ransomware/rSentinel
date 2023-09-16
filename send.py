import socket
import struct
import constants

def init_client_to_server(ip_address, port):
    try:
        # Create a new socket using the given address family and socket type.
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect the socket to the server's address and port.
        client_socket.connect((ip_address, port))
        
        return client_socket.fileno()
        
    except socket.error:
        print("\nConnection Failed \n")
        return -1

def init_client_to_server(ip_address, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_address, port))
        return client_socket
    except socket.error:
        print("\nConnection Failed \n")
        return None

def send_msg_to_demo_node(demo_address, arr, port=8080):
    client_socket = init_client_to_server(demo_address, port)
    
    if client_socket is None:
        print("Issue creating a socket")
        return

    buffer_size = len(arr)
    buffer = [socket.htonl(x) for x in arr]
    
    print(f"buffer size: {buffer_size}")
    for value in buffer:
        print(value)
    
    packed_buffer = struct.pack(f"!{buffer_size}I", *buffer)
    
    try:
        client_socket.sendall(packed_buffer)
    except socket.error:
        print("Error sending demo array")
    
    client_socket.close()


def main():
    arr = [0, 1, 0, 1, 0, 1, 1, 0]
    send_msg_to_demo_node("127.0.0.1", arr)


if __name__ == '__main__':
    main()