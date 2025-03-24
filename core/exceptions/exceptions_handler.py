from typing import List

from core.logs.log_handler import console_logger


class CustomException(Exception):
    """Base class for custom exceptions"""

    def __init__(self, message: str, status_code: int) -> None:
        """
        Constructor

        :param message: error message, ``str``
        :param status_code: error code, ``int``
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        console_logger.error(f"{message}")


class CallbackError(CustomException):
    """Base class for callback related errors"""

    pass


class CliError(CustomException):
    """Error thrown when the CLI command is invalid"""

    def __init__(self, command: str, stderr: str, rc: int) -> None:
        """
        Constructor

        :param command: command executed, ``str``
        :param stderr: error message, ``str``
        :param rc: error code, ``int``
        """
        super().__init__(
            message=f"Command executed: {command}. Error received: {stderr}. Error code: {rc}",
            status_code=400,
        )


class Base64Error(CustomException):
    """Base class for Base64 related errors"""

    def __init__(self, message: str) -> None:
        """
        Constructor

        :param message: error message, ``str``
        """
        super().__init__(message=message, status_code=500)


class FileNotFoundError(CustomException):
    """Error thrown when the file is not found"""

    def __init__(self, path: str) -> None:
        """
        Constructor

        :param path: path to the file, ``str``
        """
        super().__init__(message=f"File not found at {path}", status_code=404)


class GitError(CustomException):
    """Base class for GitHub related erros"""

    pass


class InvalidEnvVarError(CustomException):
    """Error thrown when the variables are invalid in the .env file"""

    def __init__(self, variable: str, possible_values: List[str]) -> None:
        """
        Constructor

        :param variable: variable name, ``str``
        :param possible_values: possible values for the variable, ``List[str]``
        """
        super().__init__(
            message=f"Possible values for the variable {variable} are {possible_values}",
            status_code=500,
        )


class JenkinsError(CustomException):
    """Base class for Jenkins related errors"""

    pass


class LibraryError(CustomException):
    """Base class for Library related errors"""

    pass


class ResourceManagerError(CustomException):
    """Base class for Resource Manager related errors"""

    pass


class SitesError(CustomException):
    """Base class for Sites related errors"""

    pass


class TrialNetworkError(CustomException):
    """Base class for trial network related errors"""

    pass


class UndefinedEnvVarError(CustomException):
    """Error thrown when the variables are undefined in the .env file"""

    def __init__(self, missing_variables: List[str]):
        """
        Constructor

        :param missing_variables: list of missing variables, ``List[str]``
        """
        super().__init__(
            message=f"Set the value of the variables {missing_variables} in the .env file",
            status_code=404,
        )
