# from android_cog.modules.android_battery_module import AndroidBatteryProvider
# from android_cog.modules.android_module import AndroidProvider
# from arduino_cog.modules.arduino_module import ArduinoModule
# from mission_control_cog.modules.mission_control_module import MissionControlProvider
# from up.base_system_state_recorder import BaseSystemStateRecorder
# from up.modules.base_altitude_provider import BaseAltitudeProvider
# from up.modules.base_location_provider import BaseLocationProvider
# from up.providers.black_box_controller import BaseBlackBoxStateRecorder
# from up.providers.telemetry_controller import BaseTelemetryStateRecorder
#
#
# class BlackBoxRecorder(BaseBlackBoxStateRecorder):
#     def __init__(self):
#         super().__init__()
#         self.__recorder = RaspilotSystemStateRecorder()
#
#     def initialize(self, raspilot):
#         super().initialize(raspilot)
#         self.__recorder.initialize(raspilot)
#
#     def record_state(self):
#         # self.__recorder.record_state()
#         pass
#
#
# class TelemetryRecorder(BaseTelemetryStateRecorder):
#     def __init__(self):
#         super().__init__()
#         self.__recorder = RaspilotSystemStateRecorder()
#
#     def initialize(self, raspilot):
#         super().initialize(raspilot)
#         self.__recorder.initialize(raspilot)
#
#     def record_state(self):
#         self.__recorder.record_state()
#
#
# class RaspilotSystemStateRecorder(BaseSystemStateRecorder):
#     def __init__(self):
#         super().__init__()
#         self.__mission_control = None
#         self.__arduino_module = None
#         self.__android_module = None
#         self.__android_battery_provider = None
#         self.__altitude_provider = None
#         self.__location_provider = None
#
#     def initialize(self, raspilot):
#         super().initialize(raspilot)
#         self.__mission_control = self.up.get_module(MissionControlProvider.__name__)
#         if self.__mission_control is None:
#             self.logger.critical("Mission Control Provider not found")
#             exit(1)
#         self.__altitude_provider = self.up.get_module(BaseAltitudeProvider.__name__)
#         self.__arduino_module = self.up.get_module(ArduinoModule.__name__)
#         self.__android_module = self.up.get_module(AndroidProvider.__name__)
#         self.__android_battery_provider = self.up.get_module(AndroidBatteryProvider.__name__)
#         self.__android_battery_provider = self.up.get_module(BaseLocationProvider.__name__)
#
#     def record_state(self):
#         state = {}
#         # return {'orientation': orientation, 'location': location,
#         #         'flightControllerStatus': flight_controller_status, 'altitude': altitude,
#         #         'devicesStatus': devices_status}
#
#         state['altitude'] = None
#         if self.__altitude_provider:
#             state['altitude'] = self.__altitude_provider.altitude
#
#         state['location'] = None
#         if self.__location_provider:
#             state['location'] = {
#                 'latitude': self.__location_provider.latitude,
#                 'longitude': self.__location_provider.longitude
#             }
#
#         flight_controller_status = {'cpu': None, 'batteryLevel': None, 'rx': None}
#         if self.__android_battery_provider:
#             flight_controller_status['batteryLevel'] = self.__android_battery_provider.battery_level
#         else:
#             flight_controller_status['batteryLevel'] = None
#
#         state['flightControllerStatus'] = flight_controller_status
#
#         devices_status = {'android': False, 'arduino': False}
#         if self.__android_module:
#             devices_status['android'] = self.__android_module.connected
#         if self.__arduino_module:
#             devices_status['arduino'] = self.__arduino_module.connected
#         state['devicesStatus'] = devices_status
#
#         return state
#
#     def load(self):
#         return False
