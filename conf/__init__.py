import os

from dotenv import load_dotenv
from pyfiglet import figlet_format

print(figlet_format("Trial Network Lifecycle Management", font="small"))
# TODO: add subtitulo, tamanio de la letra

dotenv_path = os.path.join(os.getcwd(), ".env")
# dotenv_path = os.path.join(os.getcwd(), ".env.dev")
load_dotenv(dotenv_path=dotenv_path)

from core.logs.log_handler import log_handler

log_handler.debug(f"Loading the '{dotenv_path}' file of TNLCM")

from .mail import MailSettings
from .mongodb import MongoDBSettings
from .jenkins import JenkinsSettings
from .repository import RepositorySettings
from .sixg_library import SixGLibrarySettings
from .sixg_sandbox_sites import SixGSandboxSitesSettings
from .tnlcm import TnlcmSettings
from .flask_conf import FlaskConf