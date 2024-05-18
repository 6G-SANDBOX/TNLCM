from dotenv import load_dotenv

from core.logs.log_handler import log_handler

log_handler.info("Loading the .env file of the project")
load_dotenv()

from .mail import MailSettings
from .mongodb import MongoDBSettings
from .jenkins import JenkinsSettings
from .repository import RepositorySettings
from .sixg_library import SixGLibrarySettings
from .sixg_sandbox_sites import SixGSandboxSitesSettings
from .tnlcm import TnlcmSettings
from .config import ProductionConfig, DevelopmentConfig, TestingConfig