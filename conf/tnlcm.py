from core.logs.log_handler import log_handler

class TnlcmSettings:
    """TNLCM Settings"""

    log_handler.info("Load TNLCM configuration")
    TITLE = "Trial Network Life Cycle Manager - TNLCM"
    VERSION = "0.2.0"
    DESCRIPTION = ("""
    Welcome to the Trial Network Life Cycle Manager (TNLCM) API! This powerful tool facilitates the management and orchestration of network life cycles, designed specifically for the cutting-edge 6G Sandbox project.

    Explore our documentation and contribute to the project's development on GitHub.\n"""
    "[6G-Sandbox - TNLCM Repository](https://github.com/6G-SANDBOX/TNLCM)")
    DOC = False
    PORT = 5000