import os

from yaml import dump
from tempfile import NamedTemporaryFile

from src.logs.log_handler import log_handler

TEMP_FILES_DIRECTORY = os.path.join(os.getcwd(), "src", "temp", "files")

class TempFileHandler:

    def __init__(self):
        """Constructor"""
        os.makedirs(TEMP_FILES_DIRECTORY, exist_ok=True)

    def create_temp_file(self, content):
        """Create temporary files for each entity that is deployed in the pipeline and returns the path to the file"""
        log_handler.info("Create temporary file to send to Jenkins pipeline")
        with NamedTemporaryFile(delete=False, dir=TEMP_FILES_DIRECTORY, suffix=".yaml", mode="w") as temp_file:
            dump(content, temp_file, default_flow_style=False)
        return temp_file.name