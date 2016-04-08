from new_raspilot.raspilot_framework.raspilot import RaspilotBuilder
from new_raspilot.raspilot_framework.utils.raspilot_logger import RaspilotLogger
from new_raspilot.raspilot_implementation.commands.stop_command import StopCommand, StopCommandHandler
from new_raspilot.raspilot_implementation.providers.android_provider import AndroidProvider

if __name__ == "__main__":
    logger = RaspilotLogger.get_logger()
    try:
        logger.info("Starting Raspilot")
        builder = RaspilotBuilder()
        builder.add_custom_provider(AndroidProvider())
        builder.with_command(StopCommand.NAME, StopCommandHandler())
        with (builder.build()) as raspilot:
            raspilot.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Stopping Raspilot")
