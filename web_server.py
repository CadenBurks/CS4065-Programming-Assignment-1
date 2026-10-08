"""
Assignment 1
Caden Burks-D'Amico
"""

from socket import *
import threading

PORT = 6789

def handle_request(connection: socket):
    """Displays contents of received message
    Args:
        connection (socket): The connection socket
    Returns:
        str: The request line of the message
    """
    file = connection.makefile()
    with file:
        request_line = file.readline()
        print(request_line)

        while True:
            header_line = file.readline()

            if not header_line.strip():
                break

            print(header_line.strip())

    connection.close()

    return request_line

def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen()
    print("Server is ready to receive")

    while True:
        connection_socket, address = server_socket.accept()
        thread = threading.Thread(target=handle_request, args=(connection_socket,))
        thread.start()

if __name__ == "__main__":
    main()
