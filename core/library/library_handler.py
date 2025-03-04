from conf.library import LibrarySettings
from core.repository.repository_handler import RepositoryHandler
from core.utils.file_handler import load_yaml
from core.utils.os_handler import exists_path, is_directory, join_path, list_directory
from core.exceptions.exceptions_handler import CustomLibraryException

class LibraryHandler:

    def __init__(
        self,
        https_url: str = None,
        reference_type: str = None, 
        reference_value: str = None,
        directory_path: str = None
    ) -> None:
        """
        Constructor
        
        :param reference_type: type of reference (branch, tag, commit) to switch, ``str``
        :param reference_value: value of the reference (branch name, tag name, commit ID) to switch, ``str``
        :param directory_path: directory path into which the Library is to be cloned, ``str``
        """
        self.library_https_url = https_url
        if https_url is None:
            self.library_https_url = LibrarySettings.LIBRARY_HTTPS_URL
        self.library_repository_name = LibrarySettings.LIBRARY_REPOSITORY_NAME
        self.library_local_directory = join_path(directory_path, self.library_repository_name)
        self.library_reference_type = reference_type
        self.library_reference_value = reference_value
        if reference_type == "branch" and reference_value:
            self.library_reference_value = reference_value
        elif reference_type == "commit" and reference_value:
            self.library_reference_value = reference_value
        elif reference_type == "tag" and reference_value:
            self.library_reference_value = f"refs/tags/{reference_value}"
        else:
            self.library_reference_type = "branch"
            self.library_reference_value = LibrarySettings.LIBRARY_BRANCH
        self.repository_handler = RepositoryHandler(github_https_url=self.library_https_url, github_repository_name=self.library_repository_name, github_local_directory=self.library_local_directory, github_reference_type=self.library_reference_type, github_reference_value=self.library_reference_value)
        self.library_commit_id = None

    def git_branches(self) -> list[str]:
        """
        Git branches

        :return: list with Library branches, ``list[str]``
        """
        return self.repository_handler.git_branches()

    def git_checkout(self) -> None:
        """
        Git checkout
        """
        self.repository_handler.git_checkout()
    
    def git_clone(self) -> None:
        """
        Git clone
        """
        self.repository_handler.git_clone()
    
    def git_pull(self) -> None:
        """
        Git pull
        """
        self.repository_handler.git_pull()

    def git_switch(self) -> None:
        """
        Git switch
        """
        self.repository_handler.git_switch()
        self.library_commit_id = self.repository_handler.github_commit_id
    
    def git_tags(self) -> list[str]:
        """
        Git tags

        :return: list with Library tags, ``list[str]``
        """
        return self.repository_handler.git_tags()
    
    def get_components(self) -> list[str]:
        """
        Function to get the available components in the Library
        
        :return components: the available components, ``list[str]``
        :raise CustomLibraryException:
        """
        components = []
        if not is_directory(path=self.library_local_directory):
            raise CustomLibraryException(f"Folder of the components is not created in commit {self.library_commit_id} of Library", 404)
        for component in list_directory(path=self.library_local_directory):
            if is_directory(path=join_path(self.library_local_directory, component)) and not component.startswith("."):
                components.append(component)
        return sorted(components)
    
    def is_component(self, component_type: str) -> None:
        """
        Function to check if component in the descriptor are in the library
        
        :param component_type: the component type to validate, ``str``
        :raise CustomLibraryException:
        """
        if component_type not in self.get_components():
            raise CustomLibraryException(f"Component {component_type} not found in Library", 404)
    
    def get_component_input(self, component_type: str) -> dict:
        """
        Function to get the input part of the component types
        
        :param component_type: the component type to get the input part, ``str``
        :return component_input: the input part of the component types, ``dict``
        :raise CustomLibraryException:
        """
        component_input = {}
        public_file_path = join_path(self.library_local_directory, component_type, ".tnlcm", "public.yaml")
        if not exists_path(path=public_file_path):
            raise CustomLibraryException(f"File {public_file_path} not found", 404)
        
        public_data = load_yaml(file_path=public_file_path)
        if public_data and "input" in public_data:
            component_input = public_data["input"]
        
        return component_input
    
    def get_component_metadata(self, component_type: str) -> dict:
        """
        Function to get the metadata part of the component types
        
        :param component_type: the component type to get the metadata part, ``str``
        :return component_metadata: the metadata part of the component types, ``dict``
        :raise CustomLibraryException:
        """
        component_metadata = {}
        public_file_path = join_path(self.library_local_directory, component_type, ".tnlcm", "public.yaml")
        if not exists_path(path=public_file_path):
            raise CustomLibraryException(f"File {public_file_path} not found", 404)
        
        public_data = load_yaml(file_path=public_file_path)
        if public_data and "metadata" in public_data:
            component_metadata = public_data["metadata"]
        
        return component_metadata
