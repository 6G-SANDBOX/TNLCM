import subprocess
from typing import Tuple

from core.exceptions.exceptions import CliError


def run_command(command: str) -> Tuple[str, str, int]:
    """
    Run a command in the shell and return the result

    :param command: the command to run, ``str``
    :return: the stdout, stderr and return code of the command, ``Tuple[str, str, int]``
    :raise CliError: if the command fails
    """
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    rc = result.returncode
    if rc != 0:
        raise CliError(command=command, stderr=stderr, rc=rc)
    return stdout, stderr, rc
