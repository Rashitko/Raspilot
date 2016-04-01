import json
import os
import socket

import raspilot_implementation.main

PIDS_PATH = "../tmp/"

HOST = ''
PORT = 3002


class RaspilotRunner:
    """
    Helper class which spawns the Raspilot instance upon receiving the request to do so. Only one instance of Raspilot
    can be spawned at any time.
    """

    def __init__(self):
        self.__run = True
        self.__socket = None

    def __receive_loop(self):
        """
        Receives requests and spawns the Raspilot
        :return: returns nothing
        """
        while self.__run:
            print("Awaiting connection...")
            self.__connection, self.__address = self.__socket.accept()
            data = self.__connection.recv(1024)
            print("Request from {}. Running Raspilot".format(self.__address))
            raspilot_implementation.main.run_raspilot(self)
            self.__connection.close()
            self.__connection = None
            self.__address = None

    def raspilot_ready(self):
        """
        Callback method, called when Raspilot is ready, replies to the client
        :return: returns nothing
        """
        if self.__connection:
            data = {'message': 'Raspilot ready', 'spawned': True, 'error': None, 'myAddress': self.__address[0]}
            serialized_data = json.dumps(data) + '\n'
            raw_data = bytes(serialized_data.encode('utf-8'))
            self.__connection.send(raw_data)

    def start(self):
        """
        Creates the socket and starts the receive loop
        :return:
        """
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind((HOST, PORT))
            self.__socket.listen(1)
            self.__receive_loop()

    def exit(self):
        """
        Closes the socket and stops the receive loop
        :return:
        """
        if self.__socket:
            self.__socket.close()
        self.__run = False


if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    pids_dir = os.path.join(dir, PIDS_PATH)
    runner = RaspilotRunner()
    try:
        runner.start()
    except KeyboardInterrupt:
        pass
    finally:
        runner.exit()
