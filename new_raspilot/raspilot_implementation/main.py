from new_raspilot.core.raspilot import RaspilotBuilder
from new_raspilot.core.utils.raspilot_loader import RaspilotLoader
from new_raspilot.core.utils.raspilot_logger import RaspilotLogger
from new_raspilot.modules.android_battery_provider import AndroidBatteryProvider
from new_raspilot.modules.android_provider import AndroidProvider
from new_raspilot.modules.flight_control import RaspilotFlightControlProvider
from new_raspilot.modules.location_provider import RaspilotLocationProvider
from new_raspilot.modules.orientation_provider import RaspilotOrientationProvider
from new_raspilot.raspilot_implementation.commands.stop_command import StopCommand, StopCommandHandler
from new_raspilot.recorders.load_guard import RaspilotLoadGuardStateRecorder
from new_raspilot.recorders.system_state_recorder import RaspilotSystemStateRecorder

if __name__ == "__main__":
    logger = RaspilotLogger.get_logger()
    try:
        with (RaspilotLoader().create()) as raspilot:
            raspilot.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Stopping Raspilot")
