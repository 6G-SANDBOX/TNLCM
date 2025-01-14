import os

from dotenv import load_dotenv
from pyfiglet import figlet_format

print(figlet_format("Trial Network Lifecycle Management", font="small"))

dotenv_path = os.path.join(os.getcwd(), ".env")
# dotenv_path = os.path.join(os.getcwd(), ".env.dev")
load_dotenv(dotenv_path=dotenv_path)

from core.logs.log_handler import tnlcm_log_handler

tnlcm_log_handler.debug(f"Loading the {dotenv_path} file of TNLCM")

from .mail import MailSettings
from .mongodb import MongoDBSettings
from .jenkins import JenkinsSettings
from .library import LibrarySettings
from .sites import SitesSettings
from .tnlcm import TnlcmSettings
from .flask_conf import FlaskConf