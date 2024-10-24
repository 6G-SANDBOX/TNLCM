import subprocess

class CliHandler:
    
    def __init__(self, command) -> None:
        self.command = command

    def run_command(self) -> dict:
        """
        Example use:
        res = run_command("echo hello!")
        if res["rc"] == 0:
            print("it worked")
        :return: dictionary with the result
        """
        try:
            result = subprocess.run(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            return_code = result.returncode
            return {"rc": return_code, "stdout": stdout, "stderr": stderr}
        except Exception as e:
            return {"rc": -1, "stdout": None, "stderr": str(e)}