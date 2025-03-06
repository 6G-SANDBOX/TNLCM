from conf.sites import SitesSettings
from core.repository.repository_handler import RepositoryHandler
from core.utils.file_handler import load_file, load_yaml, save_yaml
from core.utils.os_handler import exists_path, get_absolute_path, join_path
from core.utils.parser_handler import ansible_decrypt, yaml_to_dict
from core.exceptions.exceptions_handler import CustomSitesException

SITES_PATH = get_absolute_path(__file__)
SITES_REFERENCES_TYPES = ["branch", "commit", "tag"]

class SitesHandler():

    def __init__(
        self,
        https_url: str = None,
        reference_type: str = None, 
        reference_value: str = None,
        directory_path: str = None
    ) -> None:
        """
        Constructor
        
        :param https_url: URL of the repository, ``str``
        :param reference_type: branch to switch, ``str``
        :param reference_value: value of the branch, ``str``
        :param directory_path: directory path into which the Sites is to be cloned, ``str``
        """
        self.sites_https_url = https_url
        if https_url is None:
            self.sites_https_url = SitesSettings.SITES_HTTPS_URL
        self.sites_repository_name = SitesSettings.SITES_REPOSITORY_NAME
        self.sites_local_directory = join_path(directory_path, self.sites_repository_name)
        self.sites_reference_type = reference_type
        self.sites_reference_value = reference_value
        if reference_type == "branch" and reference_value:
            self.sites_reference_value = reference_value
        elif reference_type == "commit" and reference_value:
            self.sites_reference_value = reference_value
        else:
            self.sites_reference_value = f"refs/tags/{reference_value}"
        self.repository_handler = RepositoryHandler(github_https_url=self.sites_https_url, github_repository_name=self.sites_repository_name, github_local_directory=self.sites_local_directory, github_reference_type=self.sites_reference_type, github_reference_value=self.sites_reference_value)
        self.sites_commit_id = None
    
    def git_branches(self) -> list[str]:
        """
        Git branches

        :return: list with Sites branches, ``list[str]``
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
        self.sites_commit_id = self.repository_handler.github_commit_id

    def git_tags(self) -> list[str]:
        """
        Git tags

        :return: list with Sites tags, ``list[str]``
        """
        return self.repository_handler.git_tags()
    
    def validate_sites_branch(self) -> None:
        """
        Check if branch is valid
        """
        filtered_branches = [branch for branch in self.git_branches() if branch != "main"]
        if self.sites_reference_value not in filtered_branches:
            raise CustomSitesException(f"Branch should be one: {filtered_branches}", 404)

    def validate_deployment_site(self, deployment_site: str) -> None:
        """
        Check if branch has the directory deployment site
        
        :param deployment_site: trial network deployment site, ``str``
        :raise CustomSitesException:
        """
        if not exists_path(path=join_path(self.sites_local_directory, deployment_site)):
            raise CustomSitesException(f"Branch {self.sites_reference_value} does not have the directory {deployment_site}", 404)
        core_file = join_path(self.sites_local_directory, deployment_site, "core.yaml")
        if not exists_path(path=core_file):
            raise CustomSitesException(f"File {core_file} not found in {self.sites_reference_type} reference type and {self.sites_reference_value} reference value", 404)
        encrypted_data = load_file(file_path=core_file, mode="rb", encoding=None)
        decrypted_data = ansible_decrypt(encrypted_data=encrypted_data, token=SitesSettings.SITES_TOKEN)
        decrypted_yaml = yaml_to_dict(data=decrypted_data)
        save_yaml(data=decrypted_yaml, file_path=join_path(self.sites_local_directory, deployment_site, "core_decrypt.yaml"))

    def get_site_available_components(self, deployment_site: str) -> dict:
        """
        Function to get all information of all components available on a site

        :param deployment_site: trial network deployment site, ``str``
        :return: dictionary with all information of all components available on a site, ``dict``
        :raise CustomSitesException:
        """
        decrypted_core_path = join_path(self.sites_local_directory, deployment_site, "core_decrypt.yaml")
        if not exists_path(path=decrypted_core_path):
            raise CustomSitesException(f"File {decrypted_core_path} not found", 404)
        data = load_yaml(file_path=decrypted_core_path)
        if not data or "site_available_components" not in data:
            return {}
        site_available_components = data["site_available_components"]
        return site_available_components
    
    def is_component(self, deployment_site: str, entity_name: str) -> None:
        """
        Function to check if components in the descriptor are in the site

        :param deployment_site: trial network deployment site, ``str``
        :param entity_name: name of entity, ``str``
        :raise CustomSitesException:
        """
        site_available_components = self.get_site_available_components(deployment_site=deployment_site)
        if not site_available_components:
            raise CustomSitesException(f"Site {deployment_site} does not have any components available", 404)
        if entity_name not in site_available_components:
            raise CustomSitesException(f"Component {entity_name} is not available in site {deployment_site}", 404)
    