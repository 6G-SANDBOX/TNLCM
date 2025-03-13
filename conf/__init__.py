from dotenv import load_dotenv

from core.utils.os import DOTENV_DEV_PATH, DOTENV_PATH  # noqa: F401

load_dotenv(dotenv_path=DOTENV_PATH)
# load_dotenv(dotenv_path=DOTENV_DEV_PATH)
