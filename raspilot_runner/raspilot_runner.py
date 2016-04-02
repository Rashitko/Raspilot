import logging
import os
import signal
import subprocess

from twisted.internet import reactor
from twisted.internet.endpoints import UNIXServerEndpoint, TCP4ServerEndpoint
from twisted.internet.protocol import Factory, Protocol

from raspilot_implementation.utils.raspilot_logger import RaspilotLoggerFactory

LOGGER_NAME = 'raspilot_runner'

PIDS_PATH = "../tmp/"

HOST = ''
PORT = 3002


class NewRaspilotRunner:
    def __init__(self):
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info("Starting Raspilot Runner")
        my_dir = os.path.dirname(__file__)
        unix_socket_addr = os.path.join(my_dir, "../shared/raspilot_runner.sock")

        raspilot_endpoint = UNIXServerEndpoint(reactor, unix_socket_addr)
        raspilot_endpoint.listen(RaspilotProtocolFactory(RaspilotProtocol(self)))

        spawn_endpoint = TCP4ServerEndpoint(reactor, PORT)
        spawn_endpoint.listen(RaspilotProtocolFactory(RaspilotSpawnProtocol(self)))

        self.__raspilot_process = None

    def on_raspilot_message(self):
        try:
            if self.__raspilot_process:
                self.__logger.info('Waiting for Raspilot to exit...')
                self.__raspilot_process.wait(5)
        except subprocess.TimeoutExpired:
            self.__logger.error('Killing Raspilot it because did not exit')
            self.__raspilot_process.kill()
        finally:
            self.__raspilot_process = None

    def on_spawn_request(self):
        if not self.__raspilot_process:
            self.__logger.info('Spawning new Raspilot')
            my_dir = os.path.dirname(__file__)
            raspilot_impl_dir = os.path.join(my_dir, '../raspilot_implementation/main.py')
            path_to_script = os.path.abspath(raspilot_impl_dir)
            self.__logger.debug("Running {}".format(path_to_script))
            self.__raspilot_process = subprocess.Popen(['python3', path_to_script], stdout=subprocess.DEVNULL,
                                                       stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
            self.__logger.info("Raspilot running with PID {}".format(self.__raspilot_process.pid))
        else:
            self.__logger.warning('Raspilot already running')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__raspilot_process:
            try:
                self.__logger.info("Asking Raspilot with PID {} to exit".format(self.__raspilot_process.pid))
                os.kill(self.__raspilot_process.pid, signal.SIGINT)
                self.__raspilot_process.wait(5)
                self.__logger.info("Raspilot exited")
            except subprocess.TimeoutExpired:
                self.__logger.error("Raspilot is still running, killing it")
                self.__raspilot_process.kill()


class RaspilotProtocol(Protocol):
    def __init__(self, callbacks):
        self.__callbacks = callbacks

    def dataReceived(self, data):
        self.__callbacks.on_raspilot_message()


class RaspilotSpawnProtocol(Protocol):
    def __init__(self, callbacks):
        self.__callbacks = callbacks

    def dataReceived(self, data):
        self.__callbacks.on_spawn_request()


class RaspilotProtocolFactory(Factory):
    def __init__(self, protocol):
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol


if __name__ == "__main__":
    my_dir = os.path.dirname(__file__)
    logs_path = os.path.join(my_dir, '../logs/')
    RaspilotLoggerFactory.create(LOGGER_NAME, logging.DEBUG, os.path.abspath(logs_path))
    runner = NewRaspilotRunner()
    with runner:
        reactor.run()
