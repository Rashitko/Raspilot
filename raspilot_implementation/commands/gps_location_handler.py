from raspilot.commands.base_command_handler import BaseCommandHandler

GPS_LOCATION_COMMAND_NAME = "gps.update"


class GPSLocationHandler(BaseCommandHandler):
    """
    Handler for receiving the GPS location updates.
    """

    def __init__(self, gps_provider):
        """
        Creates a new 'GPSLocationHandler'. This handler is associated with the name 'gps.update'
        :return: returns nothing
        """
        super().__init__(GPS_LOCATION_COMMAND_NAME)
        self.__gps_provider = gps_provider

    def _run_action(self, data, command_id, request, response):
        """
        Sets the current orientation as the neutral position of the plane, when both roll and pitch will be equal to 0
        :param data: currently not processed
        :return: returns None
        """
        self.__gps_provider.on_data_received(data)
        return None
