"""
ReduLogger is a simple and easy-to-use logger for logging remotely to a server and locally to the machine.
"""

# Imports
import os
import requests
import atexit
from datetime import datetime
from pathlib import Path
from requests.auth import HTTPBasicAuth
from typing import Union

__version__ = "1.0.6"

CURRENT_DIRECTORY = Path.cwd()


class RemoteLogger:
    def __init__(self,
                 local_logging: bool,
                 remote_logging: bool,
                 is_main: bool = False,
                 disable_print : bool=False,
                 server_url: str=None,
                 auth: bool=False,
                 username: str=None,
                 password: str=None,
                 local_log_file_name: str= "log",
                 local_log_path: str= "logs",
                 local_log_extension: str= "log",
                 local_multi_log: bool=False
                 ):
        """
        Initialize RemoteLogger for logging remotely to a remote server and locally.

        Default log levels are: INFO, WARNING, ERROR, CRITICAL, DEBUG.

        Args:
            local_logging (bool): If true, log locally to the local machine.
            remote_logging (bool): If true, log remotely to the server.
            is_main (bool): If true, assigns instance main. Used for multilog. Default is false
            disable_print (bool): If true, disable printing locally. Default is false
            server_url (str): URL of the server to log remotely.
            auth (bool): If true use HTTPBasicAuth to authenticate. Default is false.
            username (str): Username for authentication if enabled.
            password (str): Password for authentication if enabled.
            local_log_file_name (str): Name of the log file. Default is "log".
            local_log_path (str): Path to save the log file. Default is "logs".
            local_log_extension (str): Extension of the log file. Default is "log".
            local_multi_log (bool): If true, log to multiple files. Default is false.
        """
        # Initialize Primary Arguments
        self.local_logging = None
        self.remote_logging = remote_logging
        self.is_main = is_main
        self.disable_print = disable_print


        # Initialize Local Logging

        ## Initialize Local Log Counter

        self.log_counter_file = self._join_path_with_cwd(local_log_path, "log_counter.txt")
        self._exists_file(self.log_counter_file)

        try:  # Try to read the log counter and increment it, with default value handling if file not found
            with open(self.log_counter_file, 'r+') as f:
                self.log_counter = int(f.read() or '1')  # Use 1 if file is empty
                f.seek(0)
                f.write(str(self.log_counter + 1))
                f.truncate()  # Remove everything after the counter
        except FileNotFoundError:
            with open(self.log_counter_file, 'w') as f:
                self.log_counter = 1
                f.write(str(self.log_counter + 1))

        ## Initialize Local Log Path

        ## WARNING: The local_log_path should be declared before Multi-Log Variables else it will crash
        self.local_log_path = Path(self._join_path_with_cwd(local_log_path))
        self._exists_path(self.local_log_path)

        ## Multi-Log Variables

        self.local_multi_log = local_multi_log
        if self.local_multi_log:
            self.launch_id_path = self._generate_launch_id_path(self.local_log_path)
            self.launch_id_file = os.path.join(self.launch_id_path, "launch_id.txt")

            # Only the main instances should handle the launch ID file
            """
            Explanation of the code block: Programmatically assigns one launch ID to the main instance and reads it 
            for non-main instances and writes the next used launch ID to the file.
            """
            if self.is_main:
                try:
                    with open(self.launch_id_file, 'r+') as f:
                        self.launch_id = int(f.read() or '1')  # Use 1 if file is empty
                        f.seek(0)
                        f.write(str(self.launch_id + 1))
                        f.truncate()
                except FileNotFoundError:
                    with open(self.launch_id_file, 'w') as f:
                        self.launch_id = 1
                        f.write(str(self.launch_id + 1))
            else:
                try:
                    with open(self.launch_id_file, 'r') as f:
                        self.launch_id = int(f.read().strip() or '1')
                except FileNotFoundError:
                    self.launch_id = 1

        ## Initialize Variables

        self.local_logging = local_logging
        self.local_log_file_name = local_log_file_name
        self._local_log_extension = local_log_extension.replace(".", "").lower()  # Remove dot
        self.local_log_extension = self._local_log_extension
        self.log_launch_id_name = f"_launchID-{self.launch_id}" if self.local_multi_log else ""
        self.local_log_file = Path.joinpath(self.local_log_path,
                                           f"{self.local_log_file_name}_{self.log_counter}{self.log_launch_id_name}.{self.local_log_extension}")


        # Initialize Remote Logging
        if self.remote_logging:
            self.server_url = server_url
            self.auth = auth
            if self.server_url and self.auth:
                if not username:
                    self.remote_logging = False
                    self.warning(f"Remote logging disabled. Authentication was enabled but username is empty")
                else:
                    self.username = username
                    self.password = password or ""


        # Register the exit function to log when the program finishes
        atexit.register(self._log_at_exit)

        # Log the initialization
        self.info(f"Logger initialized. ReduLogger Version: {__version__}")
        self.info(f"Remote logging: {self.remote_logging}")
        self.info(f"Local logging: {self.local_logging}")

    def _log_at_exit(self):
        """
        Log an info level message when the logger exits, indicating safe exit.
        """
        self.info("Logger exited safely.")

    def _log(self, level, message):
        """
        Send a log with timestamp, level and message to the remote server.

        :param level: Level of the log.
        :param message: Message of the log.
        :raises requests.exceptions.RequestException: If there's an issue with the network connection or if the server
            can't be reached.
        """
        log_data = f"{datetime.now().isoformat()} - {level}: {message}"
        json_data = {"log": log_data}

        # Write log remotely
        timeout = 5.0
        if self.remote_logging and self.server_url:
            try:
                if self.auth:
                    response = requests.post(self.server_url, json=json_data,
                                             auth=HTTPBasicAuth(self.username, self.password), timeout = timeout)
                    response.raise_for_status()
                else:
                    response = requests.post(self.server_url, json=log_data, timeout = timeout)
                    response.raise_for_status()
            except requests.exceptions.Timeout as e:
                print(f"Timeout on writing remote log to server")
            except requests.exceptions.RequestException as e:
                print(f"Failed to write remote log to server: {e}")

        # Write log locally
        if self.local_logging:
            try:
                with open(self.local_log_file, 'a') as log_file:
                    log_file.write(f"{log_data}\n")
            except Exception as e:
                print(f"Failed to write log locally: {e}")

    @staticmethod
    def _exists_path(path):
        """
        Checks if the folder exists. If not, it creates the folder.

        :param path: The path to be checked.
        """
        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _exists_file(file_path):
        """
        Checks if the file exists. If not, it creates the file.

        :param file_path: The path to the file to be checked.
        """
        try:
            file_path = Path(file_path)
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
        except Exception as e:
            print(f"Error ensuring file exists: {e}")

    @staticmethod
    def _generate_launch_id_path(log_path: Path):
        # Traverse up until we reach the "logs" folder
        for parent in [log_path] + list(log_path.parents):
            if parent.name == "logs":
                launch_id_path = str(parent)
                break
        else:
            launch_id_path = str(log_path)  # Fallback to current path
        return launch_id_path

    @staticmethod
    def _join_path_with_cwd(*paths: Union[str, Path]):
        """
        Join the given paths with the root directory.

        Args:
            paths: Paths to join.

        Returns:
            Joined path.
        """
        joined_path = Path.joinpath(CURRENT_DIRECTORY, *paths)
        return str(joined_path)

    def info(self, message, print_message: bool = False):
        """
        Send a log as INFO level

        :param message: Message of the log
        :param print_message: Prints the message to the console if True. Default is False
        """
        self._log("INFO", message)
        if print_message and not self.disable_print:
            print(f"[INFO] {message}")

    def warning(self, message, print_message: bool = False):
        """
        Send a log as WARNING level

        :param message: Message of the log
        :param print_message: Prints the message to the console if True. Default is False
        """
        self._log("WARNING", message)
        if print_message and not self.disable_print:
            print(f"[WARNING] {message}")

    def error(self, message, print_message: bool = False):
        """
        Send a log as ERROR level

        :param message: Message of the log
        :param print_message: Prints the message to the console if True. Default is False
        """
        self._log("ERROR", message)
        if print_message and not self.disable_print:
            print(f"[ERROR] {message}")

    def critical(self, message, print_message: bool = False):
        """
        Send a log as CRITICAL level

        :param message: Message of the log
        :param print_message: Prints the message to the console if True. Default is False
        """
        self._log("CRITICAL", message)
        if print_message and not self.disable_print:
            print(f"[CRITICAL] {message}")

    def debug(self, message, print_message: bool = False):
        """
        Send a log as DEBUG level

        :param message: Message of the log
        :param print_message: Prints the message to the console if True. Default is False
        """
        self._log("DEBUG", message)
        if print_message and not self.disable_print:
            print(f"[DEBUG] {message}")

    def connection(self, message, print_message: bool = False):
        """
        Send a log as CONNECTION level

        :param message: Message of the log
        :param print_message: Prints the message to the console if True. Default is False
        """
        self._log("CONNECTION", message)
        if print_message and not self.disable_print:
            print(f"[CONNECTION] {message}")
