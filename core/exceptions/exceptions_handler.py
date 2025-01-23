from core.logs.log_handler import tnlcm_log_handler

class CustomException(Exception):
    """Base class for custom exceptions"""
    def __init__(self, message: str, error_code: int):
        """
        Constructor

        :param message: error message, ``str``
        :param error_code: error code, ``int``
        """
        super().__init__(message)
        self.error_code = error_code
        tnlcm_log_handler.error(f"Error {self.error_code}: {message}")

class InvalidEnvVariableError(CustomException):
    """Error thrown when the variables are invalid in the .env file"""
    def __init__(self, variable, possible_values):
        message = f"Possible values for the variable {variable} are {possible_values}"
        super().__init__(message, 500)

class UndefinedEnvVariableError(CustomException):
    """Error thrown when the variables are undefined in the .env file"""
    def __init__(self, missing_variables):
        message = f"Set the value of the variables {missing_variables} in the .env file"
        super().__init__(message, 500)

class CustomMongoDBException(CustomException):
    """Base class for MongoDB related exceptions"""
    pass

class CustomCallbackException(CustomException):
    """Base class for callback related exceptions"""
    pass

class CustomLibraryException(CustomException):
    """Base class for Library related exceptions"""
    pass

class CustomSitesException(CustomException):
    """Base class for Sites related exceptions"""
    pass

class CustomGitException(CustomException):
    """Base class for GitHub related exceptions"""
    pass

class CustomTrialNetworkException(CustomException):
    """Base class for trial network related errors"""
    pass

class CustomJenkinsException(CustomException):
    """Base class for Jenkins related exceptions"""
    pass

class CustomResourceManagerException(CustomException):
    """Base class for resource manager related exceptions"""
    pass