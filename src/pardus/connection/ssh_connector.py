from _socket import gaierror
from logging import Logger, getLogger
from typing import Optional

from paramiko.channel import ChannelFile
from paramiko.client import SSHClient, AutoAddPolicy

from pardus.connection.model_connector import ModelConnector


class SSHConnector(ModelConnector):
    def __init__(self, address: str, port: int, user: str, passwd: str, logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        self.address = address
        self.port = port
        self.user = user
        self.passwd = passwd
        self.client = self.connect()

    def __del__(self):
        self.close()

    def close(self):
        try:
            if self.client is not None:
                self.client.close()
                del self.client
        except Exception as e:
            self.logger.warning(e)

    def connect(self) -> SSHClient:
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            client.connect(
                hostname=self.address, port=self.port,
                username=self.user, password=self.passwd,
            )
            return client
        except gaierror as e:
            self.logger.error(e)
            raise ValueError(e)

    def _validate(self, stderr):
        # https://stackoverflow.com/questions/35266753/paramiko-python-module-hangs-at-stdout-read
        pass
        # error = stderr.read().decode()
        # if error:
        #     for line in error.split("\n"):
        #         if line:
        #             if line.startswith("W:") or line.startswith("WARNING:"):
        #                 self.logger.warning(line)
        #             if line.startswith("E:") or line.startswith("ERROR:"):
        #                 self.logger.warning(line)
        #                 raise CommandError(error)

    def run(self, command: str) -> ChannelFile:
        stdin, stdout, stderr = self.client.exec_command(command)
        self._validate(stderr)

        return stdout

    def sudo_run(self, command: str, passwd: Optional[str] = None) -> ChannelFile:
        if passwd is None:
            passwd_to_use = self.passwd
        else:
            passwd_to_use = passwd

        sudo_command = f"sudo -S -p '' su -c \"{command}\""
        stdin, stdout, stderr = self.client.exec_command(sudo_command)
        stdin.write(passwd_to_use + "\n")
        stdin.flush()
        self._validate(stderr)
        return stdout
