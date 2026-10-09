"""
Assignment 1
Caden Burks-D'Amico
"""

from socket import *
import threading
import os
from ftp_client import FtpClient

PORT = 6789
CRLF = "\r\n"
USER = "caden"
PASSWORD = "burks"

def content_type(file_name: str):
    """
    Returns MIME type of a file.
    Args:
        file_name (str): The file name
    Returns:
        str: MIME type of the input as a string
    """
    if file_name.endswith((".htm", ".html")):
        return "text/html"
    if file_name.endswith((".GIF", ".gif")):
        return "image/gif"
    if file_name.endswith((".JPEG", ".jpeg", ".JPG", ".jpg")):
        return "image/jpeg"
    if file_name.endswith((".TXT", ".txt")):
        return "text/plain"
    return "application/octet-stream"
    

def send_bytes(file , connection: socket):
    """
    Writes file in 1K bytes to socket output stream.
    Args:
        file (BufferedReader): The file object
        connection (socket): The connection socket
    """
    while True:
        chunk = file.read(1024)

        if not chunk:
            break

        connection.sendall(chunk)

def handle_request(connection: socket):
    """
    Displays contents of received message and the response message to be sent.
    Args:
        connection (socket): The connection socket
    """
    file = connection.makefile()
    with file:
        request_line = file.readline()
        if not request_line:
            connection.close()
            return

        print("Request:\n------------")
        print(request_line.strip())
        while True:
            header_line = file.readline()

            if not header_line.strip():
                break

            print(header_line.strip())
        print("\n------------\n")

    request_tokens = request_line.split(" ")
    file_name = "." + request_tokens[1]

    file_exists = os.path.isfile(file_name)

    status_line = ""
    content_type_line = ""
    entity_body = ""
    if file_exists:
        status_line = "HTTP/1.0 200 OK" + CRLF
        content_type_line = "Content-type: " + content_type(file_name) + CRLF
    else:
        if content_type(file_name) != "text/plain":
            status_line = "HTTP/1.0 404 Not Found" + CRLF
            content_type_line = "Content-type: text/html" + CRLF
            entity_body = "<HTML>" + "<HEAD><TITLE>Not Found</TITLE></HEAD>" + "<BODY>Not Found</BODY></HTML>"
        else:
            status_line = "HTTP/1.0 200 OK" + CRLF
            content_type_line = "Content-type: " + content_type(file_name) + CRLF
            
            # Create an instance of ftp client
            client = FtpClient()

            # Connect to the FTP server
            client.connect(USER, PASSWORD)

            # Retrieve the file from the FTP server, remember you need to
            # first upload this file to the FTP server under your user
            # FTP directory
            client.get_file(file_name)

            # Disconnect from FTP server
            client.disconnect()

            # Assign input stream to read the recently FTP-downloaded file
            file_exists = os.path.isfile(file_name)


    print()
    print("Response:\n------------")
    print(status_line.strip())
    print(content_type_line.strip())
    if entity_body:
        print(entity_body)
    print("\n------------\n")

    connection.sendall(status_line.encode())
    connection.sendall(content_type_line.encode())
    connection.sendall(CRLF.encode())

    if file_exists:
        with open(file_name, "rb") as file:
            send_bytes(file, connection)
    else:
        connection.sendall(entity_body.encode())

    connection.close()

def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen()
    print("Server is listening...")

    while True:
        connection_socket, address = server_socket.accept()
        thread = threading.Thread(target=handle_request, args=(connection_socket,))
        thread.start()

if __name__ == "__main__":
    main()
