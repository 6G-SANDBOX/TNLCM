from core.logs.log_handler import log_handler

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
        log_handler.error(f"Error {self.error_code}: {message}")

###################################
###### Environment exception ######
###################################
class UndefinedEnvVariableError(CustomException):
    """Error thrown when the variables are undefined in the .env file"""
    def __init__(self, missing_variables):
        message = f"Set the value of the variables {', '.join(missing_variables)} in the .env file"
        super().__init__(message, 500)

###################################
######## MongoDB exception ########
###################################
class CustomMongoDBException(CustomException):
    """Base class for MongoDB related exceptions"""
    pass

###################################
####### Callback exception ########
###################################
class CustomCallbackException(CustomException):
    """Base class for callback related exceptions"""
    pass

###################################
###### 6G-Library exception #######
###################################
class CustomSixGLibraryException(CustomException):
    """Base class for 6G-Library related exceptions"""
    pass

###################################
### 6G-Sandbox-Sites exception ####
###################################
class CustomSixGSandboxSitesException(CustomException):
    """Base class for 6G-Sandbox-Sites related exceptions"""
    pass

###################################
######## GitHub exception #########
###################################
class CustomGitException(CustomException):
    """Base class for GitHub related exceptions"""
    pass

###################################
##### Trial Network exception #####
###################################
class CustomTrialNetworkException(CustomException):
    """Base class for trial network related errors"""
    pass

###################################
######## Jenkins exception ########
###################################
class CustomJenkinsException(CustomException):
    """Base class for Jenkins related exceptions"""
    pass

###################################
### Resource manager exception ####
###################################
class CustomResourceManagerException(CustomException):
    """Base class for resource manager related exceptions"""
    pass