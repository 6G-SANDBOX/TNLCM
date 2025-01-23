from dotenv import load_dotenv
from pyfiglet import figlet_format

from core.utils.os_handler import current_directory, join_path

print(figlet_format("Trial Network Lifecycle Management", font="small"))

dotenv_path = join_path(current_directory(), ".env")
# dotenv_path = join_path(current_directory()".env.dev")
load_dotenv(dotenv_path=dotenv_path)

from core.logs.log_handler import tnlcm_log_handler

tnlcm_log_handler.debug(f"Loading {dotenv_path} file of TNLCM")