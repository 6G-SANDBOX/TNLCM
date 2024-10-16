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

################################
###### General exceptions ######
################################
class KeyNotFoundError(CustomException):
    """Error thrown when a key in a JSON or YAML is not found"""
    pass

class CustomUnicodeDecodeError(CustomException):
    """Error thrown when there is an issue with decoding Unicode"""
    pass

class InvalidFileExtensionError(CustomException):
    """Error thrown when file does not have the correct extensions"""
    pass

class InvalidContentFileError(CustomException):
    """Error thrown when file has semantic faults"""
    pass

class CustomFileNotFoundError(CustomException):
    """Error thrown when the file not found"""
    pass

class NoResourcesAvailable(CustomException):
    """Error thrown when no resources available"""

################################
#### Environment exceptions ####
################################
class UndefinedEnvVariableError(CustomException):
    """Error thrown when the variables are undefined in the .env file"""
    def __init__(self, missing_variables):
        message = f"Set the value of the variables {', '.join(missing_variables)} in the .env file"
        super().__init__(message, 500)

class InvalidEnvVariableValueError(CustomException):
    """Error thrown when the variable has a value that is not accepted"""
    def __init__(self, message):
        super().__init__(message, 500)

class InvalidEmailError(CustomException):
    """Error thrown when invalid format email"""
    pass

###############################
###### GitHub exceptions ######
###############################
class CustomGitException(CustomException):
    """Base class for GitHub related exceptions"""
    pass

class GitCloneError(CustomGitException):
    """Error thrown when a Git clone operation fails"""
    pass

class GitCheckoutError(CustomGitException):
    """Error thrown when a Git checkout operation fails"""
    pass

class GitPullError(CustomGitException):
    """Error thrown when a Git pull operation fails"""
    pass

################################
###### MongoDB exceptions ######
################################
class CustomMongoDBException(CustomException):
    """Base class for MongoDB related exceptions"""
    pass

class MongoDBConnectionError(CustomMongoDBException):
    """Error thrown when MongoDB connection fails"""
    pass

class MongoDBCollectionError(CustomMongoDBException):
    """Error thrown when a MongoDB collection operation fails"""
    pass

###############################
#### 6G-Library exceptions ####
###############################
class CustomSixGLibraryException(CustomException):
    """Base class for 6G-Library related exceptions"""
    pass

class SixGLibraryComponentFolderNotFoundError(CustomSixGLibraryException):
    """Error thrown when component folder is not in 6G-Library"""
    pass

###############################
# 6G-Sandbox-Sites exceptions #
###############################
class CustomSixGSandboxSitesException(CustomException):
    """Base class for 6G-Sandbox-Sites related exceptions"""
    pass

class SixGSandboxSitesInvalidSiteError(CustomSixGSandboxSitesException):
    """Error thrown when site is invalid"""
    pass

class SixGSandboxSitesDecryptError(CustomSixGSandboxSitesException):
    """Errror thrown when sites file can not descrypt"""
    pass

class SixGSandboxSitesComponentsNotFoundError(CustomSixGSandboxSitesException):
    """Error thrown when no components are found in the cloned repository"""
    pass

###############################
## Trial Networks exceptions ##
###############################
class CustomTrialNetworkException(CustomException):
    """Base class for trial network related errors"""
    pass

class TrialNetworkInvalidStatusError(CustomTrialNetworkException):
    """Error thrown when an invalid status of trial network is provided"""
    pass

class TrialNetworkInvalidDescriptorError(CustomTrialNetworkException):
    """Error thrown when descriptor is incorrect"""
    pass

class TrialNetworkExists(CustomTrialNetworkException):
    """Error thrown when trial network exists in database"""
    pass

class TrialNetworkInvalidTnId(CustomTrialNetworkException):
    """Error thrown when trial network identifier not valid"""
    pass

############################
#### Jenkins exceptions ####
############################
class CustomJenkinsException(CustomException):
    """Base class for Jenkins related exceptions"""
    pass