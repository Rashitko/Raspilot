from new_raspilot.raspilot_framework.raspilot import RaspilotBuilder
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger
from new_raspilot.raspilot_implementation.providers.flight_control import RaspilotFlightControlProvider
from new_raspilot.raspilot_implementation.system_state_recorder import RaspilotSystemStateRecorder
from new_raspilot.raspilot_implementation.commands.stop_command import StopCommand, StopCommandHandler
from new_raspilot.raspilot_implementation.providers.android_provider import AndroidProvider
from new_raspilot.raspilot_implementation.providers.orientation_provider import RaspilotOrientationProvider

if __name__ == "__main__":
    logger = RaspilotLogger.get_logger()
    try:
        logger.info("Starting Raspilot")
        builder = RaspilotBuilder()
        builder.with_orientation_provider(RaspilotOrientationProvider())
        builder.add_custom_provider(AndroidProvider())
        builder.with_command(StopCommand.NAME, StopCommandHandler())
        builder.with_blackbox(RaspilotSystemStateRecorder())
        builder.with_telemetry(RaspilotSystemStateRecorder())
        builder.with_flight_control_provider(RaspilotFlightControlProvider())

        with (builder.build()) as raspilot:
            raspilot.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Stopping Raspilot")
