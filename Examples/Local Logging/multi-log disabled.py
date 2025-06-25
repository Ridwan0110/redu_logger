# Example usage of redu_logger.py  Version of the module is 1.0.5

import redu_logger

# Initialize redu_logger with configurations
local_log_path = "logs"
local_log_file_name = "log"

# Logging locally. Multi-Log Disabled.
logger = redu_logger.RemoteLogger(
    is_main=True,
    local_logging=True,
    remote_logging=False,
    local_log_path=local_log_path,
    local_log_file_name=local_log_file_name,
    local_multi_log=False,
)


def main():
    # Log some messages to demonstrate functionality
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    logger.debug("This is a debug message.")
    logger.connection("This is a connection message.")


if __name__ == '__main__':
    main()  # Calling it now will log the messages to the specified log file in the specified directory.
