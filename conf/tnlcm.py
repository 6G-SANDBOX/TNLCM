import sys

from core.logs.log_handler import log_handler
from core.exceptions.exceptions_handler import InvalidPythonVersionError

PYTHON_MIN_REQUIRED = (3, 12, 3)

class TnlcmSettings:
    """TNLCM Settings"""

    log_handler.info("Load TNLCM configuration")

    current_python_version = sys.version_info[:3]
    if current_python_version < PYTHON_MIN_REQUIRED:
        raise InvalidPythonVersionError(f"Python {PYTHON_MIN_REQUIRED} or higher is required. Current version: {current_python_version}", 404)
    
    log_handler.info(f"Current Python version: {current_python_version}")
    TITLE = "Trial Network Life Cycle Manager - TNLCM"
    VERSION = "0.2.0"
    DESCRIPTION = ("""
    Welcome to the Trial Network Life Cycle Manager (TNLCM) API! This powerful tool facilitates the management and orchestration of network life cycles, designed specifically for the cutting-edge 6G Sandbox project.

    Explore our documentation and contribute to the project's development on GitHub.\n"""
    "[6G-Sandbox - TNLCM Repository](https://github.com/6G-SANDBOX/TNLCM)")
    DOC = False
    PORT = 5000