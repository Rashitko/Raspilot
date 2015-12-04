import json
import time
import logging
from threading import Thread

DEFAULT_ERROR_LIMIT = 100


class BaseNotifier:
    """
    Class used by Raspilot to deliver periodical updates from the in-air device to the ground station.
    Message content is obtained with the BaseNotifier.prepareMessage() method, which should be overridden in
    the subclasses.
    """

    def __init__(self, update_freq, error_limit=DEFAULT_ERROR_LIMIT):
        """
        Creates a new 'BaseNotifier' which will periodically send messages to the ground device.
        :param update_freq: how often the update message should be sent, in milliseconds
        :return: returns nothing
        """
        self.__logger = logging.getLogger('raspilot.log')
        self.__update_freq = update_freq
        self.__dispatch_errors = 0
        self.__error_limit = error_limit
        self.__notify = False
        self.__raspilot = None

    def initialize(self):
        """
        Called once before start. Used to initialize the notifier
        :return: returns nothing
        """
        pass

    def start(self):
        """
        Starts the notifications.
        :return: returns nothing
        """
        if not self.__raspilot:
            raise ValueError("Raspilot must be set prior to start")
        self.__notify = True
        Thread(target=self.__notify_loop).start()

    def stop(self):
        """
        Stops the notifications.
        :return: returns nothing
        """
        self.__notify = False

    def __notify_loop(self, on_preparation_error=None, on_serialization_error=None, on_transmission_error=None):
        """
        Periodically prepares the message and then tries to send it.
        :return:
        """
        while self.__notify:
            dispatched = False
            try:
                message = self.__obtain_message()
                serialized_message = self.__try_to_serialize(message)
                dispatched = self.__dispatch_message(serialized_message)

            except MessagePreparationError as msgPrepError:
                self.__logger.error("Message preparation failed. Error was {}".format(msgPrepError.error))
                if on_preparation_error:
                    on_preparation_error()
            except MessageSerializationError as msgSerializationError:
                self.__logger.error("Message serialization failed. Error was {}".format(msgSerializationError.error))
                if on_serialization_error:
                    if not message:
                        message = None
                    on_serialization_error(message)
            except MessageTransmissionError as msgTransmissionError:
                self.__logger.error("Message failed to be sent. Error was {}".format(msgTransmissionError.error))
                if on_transmission_error:
                    if not message:
                        message = None
                    if not serialized_message:
                        serialized_message = None
                    on_transmission_error(message, serialized_message)
            except InterruptedError:
                print("InterruptedError occurred")
            finally:
                if dispatched:
                    self.__dispatch_errors = 0
                else:
                    self.__dispatch_errors += 1
                    if self.__dispatch_errors > self.__error_limit:
                        self.__logger.error("Updates error limit reached, stopping")
                        self.stop()
                try:
                    time.sleep(self.__update_freq / 1000)
                except InterruptedError:
                    pass

    def __obtain_message(self):
        """
        Calls self._prepare_message an catches all exceptions and throw MessagePreparationError instead
        :return: returns prepared message
        """
        try:
            return self._prepare_message()
        except Exception as e:
            raise MessagePreparationError(e)

    def _prepare_message(self):
        """
        Prepares the message which will be sent as an regular update. The default implementation returns None.
        :return: returns prepared message
        """
        return None

    def __try_to_serialize(self, message):
        """
        Calls self._serialize_message() and catches all exceptions and throw MessageSerializationError instead.
        :param message: message to be serialized
        :return: returns serialized message
        """
        try:
            return self._serialize_message(message)
        except Exception as e:
            raise MessageSerializationError(e)

    def _serialize_message(self, message):
        """
        Serializes the message. The default implementation serializes the message as a JSON.
        :param message: message to be serialized
        :return: serialized message
        """
        return json.dumps(message, indent=4)

    def __dispatch_message(self, message):
        """
        Calls self._send_message() an catches all exceptions and throw MessageTransmissionError instead
        :param message: serialized message which should be sent
        :return: returns returns True if message was sent, False, otherwise
        """
        try:
            sent = self._send_message(message)
        except Exception as e:
            raise MessageTransmissionError(e)
        return sent

    def _send_message(self, serialized_message, success=None, failure=None):
        """
        Sends the regular update message if message is not None. Callbacks should have one parameter - message.
        :param message: serialized message which should be sent
        :param success: success callback, if the message was successfully sent
        :param failure: failure callback, if the message transmission failed
        :return: returns True if message was sent, False, otherwise
        """
        update_sent = False
        if serialized_message and self.__raspilot.websocket_provider:
            update_sent = self.__raspilot.websocket_provider.send_telemetry_update_message(serialized_message)
            if not update_sent:
                self.__logger.warning("Update transmission failed")
        return update_sent

    @property
    def update_freq(self):
        return self.__update_freq

    @update_freq.setter
    def update_freq(self, value):
        self.__update_freq = value

    @property
    def raspilot(self):
        return self.__raspilot

    @raspilot.setter
    def raspilot(self, value):
        self.__raspilot = value


class MessagePreparationError(Exception):
    """
    Error thrown when an exception during the _prepare_message is risen.
    """

    def __init__(self, error):
        self.__error = error

    @property
    def error(self):
        return self.__error


class MessageTransmissionError(Exception):
    """
    Error thrown when an exception during the _send_message is risen.
    """

    def __init__(self, error):
        self.__error = error

    @property
    def error(self):
        return self.__error


class MessageSerializationError(Exception):
    """
    Error thrown when an exception during the _serialize_message is risen.
    """

    def __init__(self, error):
        self.__error = error

    @property
    def error(self):
        return self.__error
