from typing import Dict, List

from conf.sites import SitesSettings
from core.exceptions.exceptions_handler import SitesError
from core.repository.repository_handler import RepositoryHandler
from core.utils.file import load_yaml
from core.utils.os import exist_directory, get_absolute_path, is_file, join_path

SITES_PATH = join_path(get_absolute_path(__file__), SitesSettings.SITES_REPOSITORY_NAME)
SITES_REFERENCES_TYPES = ["branch", "commit"]


class SitesHandler:
    def __init__(
        self,
        https_url: str = None,
        reference_type: str = None,
        reference_value: str = None,
        directory_path: str = None,
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
        if directory_path is None:
            self.sites_local_directory = SITES_PATH
        else:
            self.sites_local_directory = join_path(
                directory_path, self.sites_repository_name
            )
        self.sites_reference_type = reference_type
        self.sites_reference_value = reference_value
        if reference_type == "branch" and reference_value:
            self.sites_reference_value = reference_value
        elif reference_type == "commit" and reference_value:
            self.sites_reference_value = reference_value
        elif reference_type == "tag" and reference_value:
            self.sites_reference_value = f"tags/{reference_value}"
        else:
            self.sites_reference_type = "branch"
            self.sites_reference_value = SitesSettings.SITES_BRANCH
        self.repository_handler = RepositoryHandler(
            github_https_url=self.sites_https_url,
            github_repository_name=self.sites_repository_name,
            github_local_directory=self.sites_local_directory,
            github_reference_type=self.sites_reference_type,
            github_reference_value=self.sites_reference_value,
        )

    def get_available_components_names(self, deployment_site: str) -> List[str]:
        """
        Function to get all components available in the sites

        :param deployment_site: directory of site, ``str``
        :return: list of components available in the sites, ``List[str]``
        """
        available_components = []
        site_available_components = self.get_site_available_components(
            deployment_site=deployment_site
        )
        if site_available_components:
            available_components = list(site_available_components.keys())
        return available_components

    def get_site_available_components(self, deployment_site: str) -> Dict:
        """
        Function to get all information of all components available on a site

        :param deployment_site: trial network deployment site, ``str``
        :return: dictionary with all information of all components available on a site, ``Dict``
        :raise SitesError:
        """
        sites_core_path = join_path(
            self.sites_local_directory, deployment_site, "core.yaml"
        )
        if not is_file(path=sites_core_path):
            raise SitesError(
                message=f"File {sites_core_path} not found in {self.sites_reference_type} reference type and {self.sites_reference_value} reference value",
                status_code=404,
            )
        data = load_yaml(file_path=sites_core_path)
        if not data or "site_available_components" not in data:
            return {}
        return data["site_available_components"]

    def validate_component_available_site(
        self, deployment_site: str, component_name: str
    ) -> None:
        """
        Function to check if components in the descriptor are in the site

        :param deployment_site: trial network deployment site, ``str``
        :param component_name: the component type to validate, ``str``
        :raise SitesError:
        """
        site_available_components = self.get_site_available_components(
            deployment_site=deployment_site
        )
        if not site_available_components:
            raise SitesError(
                message=f"No components available in deployment site {deployment_site}",
                status_code=404,
            )
        if component_name not in site_available_components:
            raise SitesError(
                message=f"Component {component_name} not found in deployment site {deployment_site}",
                status_code=404,
            )

    def validate_deployment_site(self, deployment_site: str) -> None:
        """
        Check if branch has the directory deployment site

        :param deployment_site: trial network deployment site, ``str``
        :raise SitesError:
        """
        if not exist_directory(
            path=join_path(self.sites_local_directory, deployment_site)
        ):
            raise SitesError(
                message=f"Branch {self.sites_reference_value} does not have the directory {deployment_site}",
                status_code=404,
            )
        sites_core_path = join_path(
            self.sites_local_directory, deployment_site, "core.yaml"
        )
        if not is_file(path=sites_core_path):
            raise SitesError(
                message=f"File {sites_core_path} not found in {self.sites_reference_type} reference type and {self.sites_reference_value} reference value",
                status_code=404,
            )
