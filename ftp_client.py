"""
Assignment 1
Caden Burks-D'Amico
"""

from socket import *
import re

SERVER_NAME = "localhost"
FTP_PORT = 21

class FtpClient():
    def __init__(self):
        self.CRLF = "\r\n"
        self.DEBUG = False
        self.control_socket = None
        self.control_reader = None
        self.current_response = ""

    def connect(self, username: str, password: str):
        """
        Connect to the FTP server
        Args:
            username (str): the username you use to login to your FTP session
            password (str): the password associated with the username
        """
        try:
            # Establish the control socket
            self.control_socket = socket(AF_INET, SOCK_STREAM)
            self.control_socket.connect((SERVER_NAME, FTP_PORT))

            # Get references to the socket input and output stream
            self.control_reader = self.control_socket.makefile("r")

            # Check if the initial response code is OK
            if self.__check_response(220):
                print("Successfully connected to FTP server")

            # Send username and password to FTP server
            self.__send_command(f"USER {username}", 331)
            self.__send_command(f"PASS {password}", 230)
        except IOError as e:
            print(f"IOError: {e}")
        except gaierror as e:
            print(f"GetAddressInfoError: {e}")

    def get_file(self, file_name: str):
        """
        Retrieve the file from FTP server after connection is established
        Args:
            file_name (str): the name of the file to retrieve
        """
        # Initialize the data port
        data_port = 0

        try:
            # Change to current (root) directory first
            self.__send_command("CWD /", 250)

            # Set to passive mode and retrieve the data port number from the response
            self.current_response = self.__send_command("PASV", 227)
            data_port = self.__extract_data_port(self.current_response)

            print(data_port)

            # Connect to the data port
            data_socket = socket(AF_INET, SOCK_STREAM)
            data_socket.connect((SERVER_NAME, data_port))

            # Download file from FTP server
            self.__send_command(f"RETR {file_name}", 150)

            # Check if the transfer was successful
            self.__check_response(226)

            # Write data on a local file
            self.__create_local_file(data_socket, file_name)

            data_socket.close()
        except gaierror as e:
            print(f"GetAddressInfoError: {e}")
        except IOError as e:
            print(f"IOError: {e}")

    def disconnect(self):
        """
        Close the FTP connection
        """
        try:
            self.control_reader.close()
            self.control_socket.close()
        except IOError as e:
            print(f"IOError: {e}")

    def __send_command(self, command: str, expected_response_code: int):
        """
        Send FTP command
        Args:
            command (str): the full command line to send to the FTP server
            expected_response_code (int): the expected response code from the FTP server
        Returns:
            str: the response line from the FTP server after sending the command
        """
        response = ""

        try:
            # Send command to the FTP server
            self.control_socket.sendall((command + self.CRLF).encode())

            # Get response from the FTP server
            response = self.control_reader.readline()
            if self.DEBUG:
                print(f"Current FTP response: {response}")

            # Check validity of response
            if not response.startswith(str(expected_response_code)):
                raise IOError(f"Bad response: {response}")
        except IOError as e:
            print(f"IOError: {e}")

        return response

    def __check_response(self, expected_code: int):
        """
        Check the validity of the FTP response, the response code should
        correspond to the expected response code
        Args:
            expected_code (int): the expected FTP response code
        Returns:
            bool: true if successful code
        """
        response_status = True

        try:
            self.current_response = self.control_reader.readline()
            if self.DEBUG:
                print(f"Current FTP response: {self.current_response}")
            if not self.current_response.startswith(str(expected_code)):
                response_status = False
                raise IOError(f"Bad response: {self.current_response}")
        except IOError as e:
            print(f"IOError: {e}")

        return response_status

    def __extract_data_port(self, response_line: str):
        """
        Given the complete FTP response line of setting data transmission mode
        to passive, extract the port to be used for data transfer
        Args:
            response_line (str): the FTP response line
        Returns:
            int: the data port number
        """
        data_port = 0
        pattern = re.compile(r"\((.*?)\)")
        matcher = pattern.search(response_line)
        string = [None] * 6

        if matcher:
            string = matcher.group(1).split(",")
        if self.DEBUG:
            print(f"Port integers: {string[4]}, {string[5]}")

        data_port = int(string[4]) * 256 + int(string[5])
        if self.DEBUG:
            print(f"Data Port: {data_port}")

        return data_port

    def __create_local_file(self, dis, file_name: str):
        """
        Create the file locally after retrieving data over the FRP data stream
        Args:
            dis: the data input stream
            file_name (str): the name of the file to create 
        """
        try:
            with open(file_name, "wb") as fos:
                while True:
                    data = dis.recv(1024)

                    if not data:
                        break

                    fos.write(data)
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
        except IOError as e:
            print(f"IOError: {e}")
