# FEATURE: Jenkins API
# from typing import Dict

# from core.exceptions.exceptions import JenkinsError
# from core.utils.cli import run_command
# from core.utils.file import loads_json

# DEFAULT_TIMEOUT = 10

# # REST Endpoints
# WHOAMI_URL = "me/api/json?depth=%(depth)s"
# JOBS_URL = "api/json?tree=jobs[name]"


# class Jenkins:
#     def __init__(
#         self,
#         url: str,
#         username: str,
#         password: str,
#         token: str,
#         timeout: int = DEFAULT_TIMEOUT,
#     ):
#         """
#         Constructor

#         :param url: URL of Jenkins server, ``str``
#         :param username: Jenkins username, ``str``
#         :param password: Jenkins password, ``str``
#         :param token: Jenkins token, ``str``
#         :param timeout: server connection timeout in secs (default: not set), ``int``
#         """
#         self.url = url
#         self.username = username
#         self.password = password
#         self.token = token
#         self.timeout = timeout

#     def get_whoami(self, depth: int = 0) -> Dict | None:
#         """
#         Get information about the user account that authenticated to
#         Jenkins. This is a simple way to verify that your credentials are
#         correct.

#         :param depth: JSON depth, ``int``
#         :returns: Information about the current user ``Dict``
#         """
#         whoami_url = f"{self.url}/{WHOAMI_URL % {'depth': depth}}"
#         command = f'curl -s -w "%{{http_code}}" -u {self.username}:{self.token} -X GET {whoami_url} --connect-timeout {self.timeout}'
#         stdout, stderr, rc = run_command(command=command)
#         stdout, status_code = stdout[:-3].strip(), stdout[-3:]
#         if rc != 0 or status_code != "200":
#             raise JenkinsError(
#                 f"Failed to get whoami. Command executed: {command}. Error received: {stderr}. Return code: {rc}"
#             )
#         return loads_json(data=stdout)

#     def clone_job(self, job_name: str, new_job_name: str) -> None:
#         """
#         Clone Jenkins job

#         :param job_name: Jenkins job name, ``str``
#         :param new_job_name: New Jenkins job name, ``str``
#         """
#         pass

#     def exist_directory(self, directory_name: str) -> bool:
#         """
#         Check if Jenkins directory exists

#         :param directory_name: Jenkins directory name, ``str``
#         :return: True if Jenkins directory exists, ``bool``
#         """
#         pass

#     def get_all_jobs(self, dir_depth: None) -> Dict:
#         """
#         Get all Jenkins jobs

#         :return: Jenkins jobs, ``Dict``
#         """

#     def get_job(self, job_name: str) -> Dict:
#         """
#         Get Jenkins job

#         :param job_name: Jenkins job name, ``str``
#         :return: Jenkins job, ``dict``
#         """
#         pass
