class CustomException(Exception):
    """Base class for custom exceptions"""
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

class VariablesNotDefinedInEnvError(CustomException):
    """Error thrown when the variables are not defined in the .env file"""
    pass

class KeyNotFoundError(CustomException):
    """Error thrown when a key in a JSON or YAML is not found"""
    pass

class CustomUnicodeDecodeError(CustomException):
    """Error thrown when there is an issue with decoding Unicode"""
    pass

class InvalidFileExtensionError(CustomException):
    """Error thrown when file does not have the correct extensions"""
    pass

class InvalidContentError(CustomException):
    """Error thrown when file has semantic faults"""
    pass

# GitHub exceptions
class CustomGitError(CustomException):
    """Base class for GitHub related exceptions"""
    pass

class GitCloneError(CustomGitError):
    """Error thrown when a Git clone operation fails"""
    pass

class GitCheckoutError(CustomGitError):
    """Error thrown when a Git checkout operation fails"""
    pass

class GitPullError(CustomGitError):
    """Error thrown when a Git pull operation fails"""
    pass

# MongoDB exceptions
class CustomMongoDBException(CustomException):
    """Base class for MongoDB related exceptions"""
    pass

class MongoDBConnectionError(CustomMongoDBException):
    """Error thrown when MongoDB connection fails"""
    pass

class MongoDBCollectionError(CustomMongoDBException):
    """Error thrown when a MongoDB collection operation fails"""
    pass

# 6GLibrary exceptions
class CustomSixGLibraryError(CustomException):
    """Base class for 6G-Library related exceptions"""
    pass

class SixGLibraryComponentsNotFound(CustomSixGLibraryError):
    """Error thrown when no components are found in the cloned repository"""
    pass

class SixGLibraryComponentNotFound(CustomSixGLibraryError):
    """Error thrown when a specific component is not found in the cloned repository"""
    pass

# Trial Networks exceptions
class CustomTrialNetworkError(CustomException):
    """Base class for trial network related errors"""
    pass

class TrialNetworkInvalidStatusError(CustomTrialNetworkError):
    """Error thrown when an invalid status of trial network is provided"""
    pass

class TrialNetworkDescriptorEmptyError(CustomTrialNetworkError):
    """Error thrown when try to save an empty descriptor"""
    pass

class TrialNetworkEntityNotInDescriptorError(CustomTrialNetworkError):
    """Error thrown when the name of the dependency does not match the name of some entity defined in the descriptor"""
    pass

# User exceptions
class CustomUserError(CustomException):
    """Base class for user related errors"""
    pass

class UserEmailInvalidError(CustomUserError):
    """Error thrown when invalid format email"""
    pass

# Jenkins exceptions
class CustomJenkinsError(CustomException):
    """Base class for Jenkins related exceptions"""
    pass

class JenkinsConnectionError(CustomJenkinsError):
    """Error thrown when unable to establish connection to Jenkins"""
    pass

class JenkinsComponentFileNotFoundError(CustomJenkinsError):
    """Error thrown when the component file with the necessary information to send is not found"""
    pass

class JenkinsResponseError(CustomJenkinsError):
    """Error thrown when request response is unsuccessful"""
    pass

class JenkinsComponentPipelineError(CustomJenkinsError):
    """Error thrown when component pipeline has failed"""
    pass

class JenkinsDeploymentReportNotFoundError(CustomJenkinsError):
    """Error thrown when the trial network report file was not found"""
    pass