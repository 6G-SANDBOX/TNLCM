from dotenv import load_dotenv

from core.utils.os_handler import current_directory, join_path

dotenv_path = join_path(current_directory(), ".env")
# dotenv_path = join_path(current_directory()".env.dev")
load_dotenv(dotenv_path=dotenv_path)