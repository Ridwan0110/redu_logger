# redu_logger
Named as "redu-logger" for pip name normalization.

[![Python](https://img.shields.io/badge/python-3.6%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/license/mit/)
[![Version](https://img.shields.io/badge/version-1.0.5-blue)](https://github.com/Ridwan0110/redu_logger/releases)
[![GitHub](https://img.shields.io/badge/source-GitHub-blue?logo=github)](https://github.com/Ridwan0110/redu_logger)


redu_logger.py is the main module file. This is a custom logger written in Python for use with Python applications and scripts. This is something I made during a personal project, and I love to share things with the world that helped me and might help someone else. This is not something advanced. It's a basic Python module for logging, and it's very manual.

## Installation

This module is not uploaded to PyPI. I uploaded it to my server. Here is the simple command you have to run in your terminal to install the latest version of redu_logger:

```
pip install redu-logger --extra-index-url https://python.ridwanabid.com/repository/simple
```

If you are worried about security, go to the [link](https://python.ridwanabid.com/repository/simple) and download the files manually. See them inside. The source code is there.

## Features

- Log any message to a specified file with log levels
- Log both locally and remotely
- Log to multiple files in local logging. A feature called Multi-Log
- Application session tracking for logs to easily understand which log files are for a specified session

## Log Levels
**Version of 'redu_logger.py' is <ins>1.0.5</ins> when writing this.**

There are now a total of 6 log levels. But you can always add custom log levels yourself.

1. Info
2. Warning
3. Error
4. Critical
5. Debug
6. Connection

## Example Implementation

### Logging locally with Multi-Log disabled:

```
# Example usage of redu_logger.py  Version of the module is 1.0.5

import redu_logger

# Initialize redu_logger with configurations
local_log_path = "logs"
local_log_file_name = "log"

# Logging locally. Multi-Log Disabled.
logger = redu_logger.RemoteLogger(
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
```

### Logging locally with Multi-Log enabled:

```
# file1
# Example usage of redu_logger.py  Version of the module is 1.0.5

import redu_logger
import subprocess
import sys

# Initialize redu_logger with configurations
local_log_path = "logs/file1"
local_log_file_name = "file1"

# Logging locally. Multi-Log Enabled.
logger = redu_logger.RemoteLogger(
    is_main=True,
    local_logging=True,
    remote_logging=False,
    local_log_path=local_log_path,
    local_log_file_name=local_log_file_name,
    local_multi_log=True,
)


def main():
    # Log some messages to demonstrate functionality
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    logger.debug("This is a debug message.")
    logger.connection("This is a connection message.")
    subprocess.run([sys.executable, "multi-log enabled (file2).py"])


if __name__ == '__main__':
    main()  # Calling it now will log the messages to the specified log file in the specified directory.
```
Notice here that the only thing changed is that a new argument `is_main` is set to True; the path of the `local_log_path`, `local_log_file_name`, and `local_multi_log` is set the True when initializing the logger.

Now, for another file, only the initialization of the logger has to be changed for Multi-Log to work properly. For example:
```
# file2
# Example usage of redu_logger.py  Version of the module is 1.0.5

# Codes...

# Initialize redu_logger with configurations
local_log_path = "logs/file2"
local_log_file_name = "file2"

# Logging locally. Multi-Log Enabled.
logger = redu_logger.RemoteLogger(
    local_logging=True,
    remote_logging=False,
    local_log_path=local_log_path,
    local_log_file_name=local_log_file_name,
    local_multi_log=True,
)

# Codes...
```
Here, the argument `is_main` is not used. This is crucial for Multi-Log to work properly. There can only be one main file, which will run the other files internally, and in their initialization of the logger, `is_main` has to be set to **False**. But we didn't set it here because it is set to **False** by default. There is more to setting up Multi-Log properly. Look into the WikI to learn more.

### Logging remotely:

I once logged remotely for my one script, but never had to then. That's why the support and the method of logging remotely are a bit complicated and manual. For remote logging to work, you need some sort of server. I used Flask, but I don't have the code on how I did that. So, until I decide to create a server script for remote logging, you have to make a server that can communicate with this module for remote logging.

## Known Issues
- Writing log entries containing Unicode emojis (e.g., 🟢, ⚪) triggers a `charmap` codec error on Windows environments if the local filesystem encoding is not explicitly set to UTF-8.
