import re
from datetime import datetime

from logging import Logger, getLogger
from typing import List, Optional, Dict, Union, Any

from pardus.apt.model_apt import ModelApt
from pardus.connection.model_connector import ModelConnector
from pardus.utils.common import escape_string
from pardus.utils.error import AlreadyExist, NotFound


def is_valid_source_line(line: str) -> None:
    pattern = re.compile(r'^(deb|deb-src)\s+'
                         r'(\[.*?\]\s+)?'
                         r'https?://\S+\s+'
                         r'\S+\s+'
                         r'(\S+.*)?$')

    if not bool(pattern.match(line.strip())):
        raise ValueError("Wrong repo line")


def option_matcher(option: str) -> Optional[Dict[str, str]]:
    if not option:
        return None

    options_to_return = {}
    options = option.strip().lstrip("[").rstrip("]")

    for option in options.split():
        key, value = option.split("=")
        options_to_return[key] = value

    return options_to_return


class Apt(ModelApt):
    def __init__(self, connector: ModelConnector, sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        self.sudo_passwd = sudo_passwd
        self.connector = connector

    def repositories(self) -> List[Dict[str, Any]]:
        output = self.connector.run("grep --no-filename -r '^deb ' /etc/apt/sources.list /etc/apt/sources.list.d/")

        pattern = re.compile(r'^(deb|deb-src)\s+'
                             r'(\[.*?\]\s+)?'
                             r'(\S+)\s+'
                             r'(\S+)\s+'
                             r'(.+)$')
        repositories = []

        repos = output.read().decode().split("\n")
        for repo in repos:
            line = repo.strip()
            match = pattern.match(line)
            if match:
                entry = {
                    'kind': match.group(1),
                    'options': option_matcher(match.group(2)),
                    'url': match.group(3),
                    'distribution': match.group(4),
                    'components': match.group(5).strip()
                }
                repositories.append(entry)

        return repositories

    def add_repository(self, repository: str) -> None:
        is_valid_source_line(repository)
        repos = self.repositories()

        search = re.search(r"(?P<url>https?://\s+)", repository)
        if search is None:
            return

        if search.group("url") in [r["url"] for r in repos]:
            raise AlreadyExist("Repo Already exist")

        self.connector.sudo_run(f"echo '# Added By Pardus @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'"
                                " >> /etc/apt/sources.list.d/pardus.list", passwd=self.sudo_passwd)
        self.connector.sudo_run(f"echo {repository} >> /etc/apt/sources.list.d/pardus.list", passwd=self.sudo_passwd)

    def update(self) -> None:
        _ = self.connector.run("apt update")

    def upgrade(self, package_name: Optional[str] = None) -> None:
        if isinstance(package_name, str):
            escape_string(package_name)
            _ = self.connector.sudo_run(f"sudo apt upgrade -y --only-upgrade {package_name}", passwd=self.sudo_passwd)
            return

        _ = self.connector.sudo_run("sudo apt upgrade -y", passwd=self.sudo_passwd)

    def list(self, installed: bool = False, upgradeable: bool = False) -> List[Dict[str, str]]:
        command = "apt list"
        if installed:
            command += " --installed"

        if upgradeable:
            command += " --upgradeable"

        packages = self.connector.run(command)

        parsed_data = []
        for line in packages.read().decode().split("\n"):
            try:

                if "/" not in line.strip():
                    continue
                package, rest = line.strip().split("/")
                exp = re.findall(r'\[[^\]]*\]|\S+', rest)
                if len(exp) == 3:
                    repo, version, arch = exp
                    tags = ""
                else:
                    repo, version, arch, tags = exp

                parsed_data.append(
                    {
                        "package": package,
                        "repo": repo,
                        "version": version,
                        "arch": arch,
                        "tags": [each.strip() for each in tags.lstrip("[").rstrip("]").split(",") if each.strip()]
                    }
                )
            except Exception as e:
                self.logger.warning(e)

        return parsed_data

    def install(self, package_name: Union[str, List[str]]) -> None:
        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" in available_packages[p]:
                self.logger.warning(f"Package `{p}` already installed. Use `reinstall`. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt install {' '.join(package_to_be_installed)} -y"
        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def reinstall(self, package_name: Union[str, List[str]]) -> None:
        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" not in available_packages[p]:
                self.logger.warning(f"Package `{p}` already installed. Use `install`. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt reinstall {' '.join(package_to_be_installed)} -y"
        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def remove(self, package_name: Union[str, List[str]]) -> None:
        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" not in available_packages[p]:
                self.logger.warning(f"Package `{p}` is not installed. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt remove {' '.join(package_to_be_installed)} -y"
        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def purge(self, package_name: Union[str, List[str]]) -> None:
        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" not in available_packages[p]:
                self.logger.warning(f"Package {p} is not installed. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt purge {' '.join(package_to_be_installed)} -y"
        _ = self.connector.sudo_run(command, passwd=self.sudo_passwd)

    def search(self, package_name: str) -> List[Dict[str, str]]:
        available_packages = {p["package"]: p["tags"] for p in self.list()}

        escape_string(package_name)

        if package_name not in available_packages.keys():
            self.logger.warning(f"Package `{package_name}` not found")
            raise NotFound(f"Package `{package_name}` not found")

        command = f"apt search {package_name}"
        stdout = self.connector.run(command)

        lines = stdout.read().decode().strip().split('\n')
        packages_to_return = []

        while lines:
            name_version_arch = lines.pop(0).strip()
            description_lines = []

            match = re.match(r'(.+?)/(.+?)\s+([\d\w.:+-]+)\s+(\S+)(?:\s+\[.*\])?', name_version_arch)
            if match:
                name, repo, version, arch = match.groups()
                description = ''

                while lines and not lines[0].startswith(' '):
                    description_lines.append(lines.pop(0).strip())

                if lines:
                    description = lines.pop(0).strip()

                packages_to_return.append({
                    'name': name,
                    'repo': repo,
                    'version': version,
                    'architecture': arch,
                    'description': description
                })

        return packages_to_return

    def show(self, package_name: str) -> Dict[Union[str, None], Any]:
        # 920
        available_packages = {p["package"]: p["tags"] for p in self.list()}

        escape_string(package_name)

        if package_name not in available_packages.keys():
            self.logger.warning(f"Package `{package_name}` not found")
            raise NotFound(f"Package `{package_name}` not found")

        command = f"apt show {package_name}"
        stdout = self.connector.run(command)

        lines = stdout.read().decode().strip().split('\n')
        parsed_dict: dict[Union[str, None], Any] = {}

        current_key = None
        for line in lines:
            if line.startswith(' '):
                parsed_dict[current_key] += '\n' + line.strip()
            else:
                key, value = line.split(': ', 1)
                current_key = key.strip()
                if current_key == 'Depends':
                    parsed_dict[current_key] = [dep.strip() for dep in value.split(',')]
                else:
                    parsed_dict[current_key] = value.strip()

        return parsed_dict
