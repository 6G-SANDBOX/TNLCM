class CustomException(Exception):
    """Base class for custom exceptions"""
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

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

class GitRequiredFieldError(CustomGitError):
    """Error thrown when only one field is required. Either git_branch or git_commit_id"""
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
class CustomSixGLibraryError(CustomException):
    """Base class for 6G-Library related exceptions"""
    pass

class SixGLibraryComponentsNotFound(CustomSixGLibraryError):
    """Error thrown when no components are found in the cloned repository"""
    pass

class SixGLibraryComponentNotFound(CustomSixGLibraryError):
    """Error thrown when a specific component is not found in the cloned repository"""
    pass

###############################
# 6G-Sandbox-Sites exceptions #
###############################
class CustomSixGSandboxSitesError(CustomException):
    """Base class for 6G-Sandbox-Sites related exceptions"""
    pass

class SixGSandboxSitesInvalidSiteError(CustomSixGSandboxSitesError):
    """Error thrown when site is invalid"""
    pass

###############################
## Trial Networks exceptions ##
###############################
class CustomTrialNetworkError(CustomException):
    """Base class for trial network related errors"""
    pass

class TrialNetworkInvalidStatusError(CustomTrialNetworkError):
    """Error thrown when an invalid status of trial network is provided"""
    pass

class TrialNetworkEntityNotInDescriptorError(CustomTrialNetworkError):
    """Error thrown when the name of the dependency does not match the name of some entity defined in the descriptor"""
    pass

class TrialNetworkInvalidComponentSite(CustomTrialNetworkError):
    """Error thrown when component not available in site"""
    pass

############################
#### Jenkins exceptions ####
############################
class CustomJenkinsError(CustomException):
    """Base class for Jenkins related exceptions"""
    pass

class JenkinsConnectionError(CustomJenkinsError):
    """Error thrown when unable to establish connection to Jenkins"""
    pass

class JenkinsResponseError(CustomJenkinsError):
    """Error thrown when request response is unsuccessful"""
    pass

class JenkinsComponentPipelineError(CustomJenkinsError):
    """Error thrown when component pipeline has failed"""
    pass

class JenkinsInvalidJobError(CustomJenkinsError):
    """Error thrown when job not in Jenkins"""
    pass