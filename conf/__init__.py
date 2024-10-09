import os

from dotenv import load_dotenv

from core.logs.log_handler import log_handler

dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv_path_dev = os.path.join(os.getcwd(), ".env.dev")
log_handler.info(f"Loading the '{dotenv_path}' file of the project")
load_dotenv(dotenv_path=dotenv_path)

from .mail import MailSettings
from .mongodb import MongoDBSettings
from .jenkins import JenkinsSettings
from .repository import RepositorySettings
from .sixg_library import SixGLibrarySettings
from .sixg_sandbox_sites import SixGSandboxSitesSettings
from .tnlcm import TnlcmSettings
from .config import ProductionConfig, DevelopmentConfig, TestingConfig