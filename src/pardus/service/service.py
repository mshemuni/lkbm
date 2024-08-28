import re
from datetime import datetime
from logging import Logger, getLogger
from typing import Optional, List, Dict, Union, Self

from pardus.connection.model_connector import ModelConnector
from pardus.service.model_service import ModelService
from pardus.utils.common import escape_string
from pardus.utils.error import NotFound


class Service(ModelService):
    def __init__(self, connector: ModelConnector, sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        self.sudo_passwd = sudo_passwd
        self.connector = connector

    def check(self, service: str):
        services = [service["unit"] for service in self.list()]
        if service not in services:
            raise NotFound("No service was found with the given name")

    def list(self) -> List[Dict[str, str]]:
        command = "systemctl list-units -all --no-pager --no-legend | tr -cd '\11\12\15\40-\176'"
        stdout = self.connector.run(command)

        table_to_return = []
        for row in stdout.read().decode().split("\n"):
            if row:
                columns = row.split()
                table_to_return.append(
                    {
                        "unit": columns[0],
                        "load": columns[1],
                        "active": columns[2],
                        "substate": columns[3],
                        "description": " ".join(columns[4:])
                    }
                )

        return table_to_return

    def start(self, service: str) -> None:
        self.check(service)

        escape_string(service)
        command = f"systemctl start {service}"

        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def stop(self, service: str) -> None:
        self.check(service)

        escape_string(service)
        command = f"systemctl stop {service}"
        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def restart(self, service: str) -> None:
        self.check(service)

        escape_string(service)
        command = f"systemctl restart {service}"

        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def enable(self, service: str) -> None:
        self.check(service)

        escape_string(service)
        command = f"systemctl enable {service}"

        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def disable(self, service: str) -> None:
        self.check(service)

        escape_string(service)
        command = f"systemctl disable {service}"

        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def logs(self, service) -> List[Dict[str, Union[str, datetime]]]:
        self.check(service)

        escape_string(service)
        command = f"journalctl -u {service} -b -o short-iso"

        stdout = self.connector.run(command)

        parsed_log = []
        log_pattern = re.compile(r'(?P<timestamp>[\d\-T:+]+)\s+(?P<domain>\S+)\s+systemd\[\d+\]:\s+(?P<message>.+)')

        for line in stdout.read().decode().strip().splitlines():
            match = log_pattern.match(line)
            if match:
                entry = {

                    'timestamp': datetime.strptime(match.group('timestamp'), "%Y-%m-%dT%H:%M:%S%z"),
                    'domain': match.group('domain'),
                    'message': match.group('message')
                }
                parsed_log.append(entry)

        return parsed_log
