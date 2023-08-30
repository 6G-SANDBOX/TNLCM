from paramiko import SSHClient, AutoAddPolicy
from shared.data import TrialNetwork
from .base_task import BaseTask


class SSH(BaseTask):
    def __init__(self, tn: TrialNetwork, rawConfig: {}):
        super().__init__(tn, rawConfig)

        self.host = self.config['Host']
        self.user = self.config['User']
        self.password = self.config['Password']
        self.command = self.config['Command']

    def Run(self):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(self.host, username=self.user, password=self.password)
        stdin, stdout, stderr = client.exec_command(self.command)
        stdout.channel.set_combine_stderr(True)
        self.output(stdout)
        exit_status = stdout.channel.recv_exit_status()
        print(str(exit_status))

    def output(self, pipe):
        for line in iter(pipe.readline, ''):  # paramiko already converts to str
            print(line, end='')
            self.internalLog.append(line)
