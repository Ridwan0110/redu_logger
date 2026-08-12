"""
AI Generated. Tweaked by human
"""
# Imports
import pytest
import atexit
from unittest.mock import patch
from requests.auth import HTTPBasicAuth

# Import the internal module directly for monkeypatching, and public API for assertions
try:
    import redu_logger.redu_logger as rl_module
    from redu_logger import RemoteLogger, __version__
except ImportError:
    import redu_logger as rl_module
    from redu_logger import RemoteLogger, __version__


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """
    Redirects CWD and module-level CURRENT_DIRECTORY to a temporary directory
    so tests do not write files into your real working directory.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(rl_module, "CURRENT_DIRECTORY", tmp_path)
    return tmp_path

@pytest.fixture(autouse=True)
def cleanup_at_exit():
    """
    Without this function, both ``test_remote_logging_unauthenticated()`` and ``test_remote_logging_authenticated()``
    will try to send POST request atexit

    :return:
    """
    yield
    atexit._clear()


# ============================================================================
# 1. VERSION & INITIALIZATION TESTS
# ============================================================================

def test_version():
    """Verify package version is set."""
    assert __version__ == "1.1.0"


def test_logger_initialization_defaults(temp_env):
    """Test initializing RemoteLogger with basic defaults."""
    logger = RemoteLogger(local_logging=True, remote_logging=False)

    assert logger.local_logging is True
    assert logger.remote_logging is False
    assert logger.disable_print is False
    assert logger.local_log_file.exists()
    assert logger.local_log_file.name == "log_1.log"


# ============================================================================
# 2. LOG COUNTER TESTS
# ============================================================================

def test_log_counter_incrementation(temp_env):
    """Test sequential counter increments across logger instances."""
    logger1 = RemoteLogger(local_logging=True, remote_logging=False)
    assert logger1.log_counter == 1

    logger2 = RemoteLogger(local_logging=True, remote_logging=False)
    assert logger2.log_counter == 2

    logger3 = RemoteLogger(local_logging=True, remote_logging=False)
    assert logger3.log_counter == 3

def test_log_counter_corrupted_file(temp_env):
    """Test counter behavior when the counter file contains invalid text."""
    log_folder = temp_env / "logs"
    log_folder.mkdir(exist_ok=True)
    counter_file = log_folder / "log_counter.txt"
    counter_file.write_text("invalid_number_string")

    logger = RemoteLogger(local_logging=True, remote_logging=False)
    assert logger.log_counter == 1

def test_log_counter_corrupted_file_after_initialization(temp_env):
    """Test counter behavior when the counter file contains invalid text after an initialization."""
    RemoteLogger(local_logging=True, remote_logging=False)

    log_folder = "logs"
    counter_file = temp_env / log_folder / "log_counter.txt"
    counter_file.write_text("invalid_number_string")

    logger = RemoteLogger(local_logging=True, remote_logging=False)
    assert logger.log_counter == 1



# ============================================================================
# 3. LOCAL FILE PATH & MULTI-LOG TESTS
# ============================================================================

def test_single_log_filepath(temp_env):
    """Test path resolution for single log mode."""
    logger = RemoteLogger(
        local_logging=True,
        remote_logging=False,
        local_log_file_name="app",
        local_log_path="custom_logs",
        local_log_extension="txt",
        local_multi_log=False
    )
    expected_path = temp_env / "custom_logs" / "app_1.txt"
    assert logger.local_log_file == expected_path
    assert expected_path.exists()


def test_multi_log_filepath(temp_env):
    """Test path resolution for multi log mode (launch_X folder structure)."""
    logger = RemoteLogger(
        local_logging=True,
        remote_logging=False,
        local_log_file_name="session",
        local_log_path="logs",
        local_log_extension="log",
        local_multi_log=True
    )
    expected_path = temp_env / "logs" / "session_1_launchID-1.log"
    assert logger.local_log_file == expected_path
    assert expected_path.exists()


# ============================================================================
# 4. LOG LEVEL EMISSION TESTS
# ============================================================================

@pytest.mark.parametrize("method_name,level_str", [
    ("info", "INFO"),
    ("warning", "WARNING"),
    ("error", "ERROR"),
    ("critical", "CRITICAL"),
    ("debug", "DEBUG"),
    ("connection", "CONNECTION"),
])
def test_local_log_levels(temp_env, method_name, level_str):
    """Test writing log entries for every log level."""
    logger = RemoteLogger(local_logging=True, remote_logging=False)
    log_func = getattr(logger, method_name)

    message = f"Testing level {level_str}"
    log_func(message)

    content = logger.local_log_file.read_text()
    assert f"{level_str}: {message}" in content


# ============================================================================
# 5. STACK TRACING (_who_called_me) TESTS
# ============================================================================

def test_who_called_me_trace_levels(temp_env):
    """Test that specifying trace_levels records frame caller info in debug level."""
    logger = RemoteLogger(local_logging=True, remote_logging=False)

    logger.info("Trace message", trace_levels=2)

    content = logger.local_log_file.read_text()
    assert "Stack Trace:" in content
    assert "test_redu_logger.py" in content


def test_who_called_me_invalid_or_none_levels(temp_env):
    """Test stack tracing behavior when trace_levels is None or 0."""
    logger = RemoteLogger(local_logging=True, remote_logging=False)

    trace = logger._who_called_me(depth=None)
    assert trace == []

    trace = logger._who_called_me(depth=99999)
    assert trace == []


# ============================================================================
# 6. CONSOLE OUTPUT (PRINT) TESTS
# ============================================================================

def test_console_print_enabled(temp_env, capsys):
    """Test printing to console when print_message=True."""
    logger = RemoteLogger(local_logging=True, remote_logging=False, disable_print=False)
    logger.info("Hello Console", print_message=True)

    captured = capsys.readouterr()
    assert "[INFO] Hello Console" in captured.out


def test_console_print_disabled_globally(temp_env, capsys):
    """Test that disable_print=True suppresses output even if print_message=True."""
    logger = RemoteLogger(local_logging=True, remote_logging=False, disable_print=True)
    logger.info("Hidden Message", print_message=True)

    captured = capsys.readouterr()
    assert captured.out == ""


# ============================================================================
# 7. REMOTE LOGGING TESTS (MOCKED)
# ============================================================================

@patch("requests.post")
def  test_remote_logging_unauthenticated(mock_post, temp_env):
    """Test remote logging HTTP POST without basic auth."""
    mock_post.return_value.status_code = 200

    server_url = "https://example.com/api/logs"
    logger = RemoteLogger(
        local_logging=False,
        remote_logging=True,
        server_url=server_url,
        auth=False
    )

    # Clear the 3 initialization calls made during RemoteLogger.__init__
    mock_post.reset_mock()

    logger.info("Remote Test Message")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == server_url
    assert "INFO: Remote Test Message" in kwargs["json"]["log"]
    assert "auth" not in kwargs


@patch("requests.post")
def test_remote_logging_authenticated(mock_post, temp_env):
    """Test remote logging HTTP POST with basic authentication."""
    mock_post.return_value.status_code = 200

    server_url = "https://example.com/api/logs"
    logger = RemoteLogger(
        local_logging=False,
        remote_logging=True,
        server_url=server_url,
        auth=True,
        username="admin",
        password="secretpassword"
    )

    # Clear the 3 initialization calls made during RemoteLogger.__init__
    mock_post.reset_mock()

    logger.error("Auth Test Error")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == server_url
    assert "ERROR: Auth Test Error" in kwargs["json"]["log"]
    assert isinstance(kwargs["auth"], HTTPBasicAuth)
    assert kwargs["auth"].username == "admin"
    assert kwargs["auth"].password == "secretpassword"


# ============================================================================
# 8. EXIT HANDLER TEST
# ============================================================================

def test_at_exit_handler(temp_env):
    """Test that calling _at_exit appends the exit message."""
    logger = RemoteLogger(local_logging=True, remote_logging=False)
    logger._log_at_exit()

    content = logger.local_log_file.read_text()
    assert "INFO: Logger exited safely." in content
