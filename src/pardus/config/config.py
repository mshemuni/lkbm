import configparser
import io
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional, Union, Dict, Any

from pardus.config.model_config import ModelConfig
from pardus.connection.model_connector import ModelConnector


class Config(Dict[str, Any], ModelConfig):
    def __init__(self, connector: ModelConnector, path: Union[str, Path],
                 create: bool = False, backup: bool = False, force: bool = False,
                 sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        if isinstance(path, Path):
            self.path = path
        else:
            self.path = Path(path)

        self.connector = connector
        self.sudo_passwd = sudo_passwd

        if not self.exist():
            if not create:
                raise FileNotFoundError("Config file does not exist")
            else:
                self.touch()

        if backup:
            self.create_backup()

        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read_string(self.read())

        super().__init__({section: dict(self.config.items(section)) for section in self.config.sections()})

    def __setitem__(self, key: str, value: Dict[str, str]) -> None:
        super().__setitem__(key, value)
        self.__update()

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key)
        self.__update()

    def clear(self) -> None:
        super().clear()
        self.__update()

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self.__update()

    def touch(self) -> None:
        _ = self.connector.sudo_run(
            f"mkdir -p {self.path.parent.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = self.connector.sudo_run(f"touch {self.path.absolute().__str__()}", passwd=self.sudo_passwd)

    def exist(self, the_file: Optional[Union[str, Path]] = None) -> bool:
        if the_file is None:
            file_to_check = self.path
        else:
            if isinstance(the_file, Path):
                file_to_check = the_file
            else:
                file_to_check = Path(the_file)

        stdout = self.connector.run(f"test -e {file_to_check} && echo exist")
        return "e" in stdout.read().decode()

    def create_backup(self) -> None:
        backup_base = self.path.parent / (self.path.name + ".0")

        counter = 1
        while self.exist(backup_base):
            backup_base = backup_base.parent / (backup_base.stem + f".{counter}")
            counter += 1

        _ = self.connector.sudo_run(
            f"cp {self.path.absolute().__str__()} {backup_base.absolute().__str__()}", passwd=self.sudo_passwd
        )

    def read(self) -> str:
        stdout = self.connector.sudo_run(f"cat {self.path.absolute().__str__()}", passwd=self.sudo_passwd)
        return str(stdout.read().decode())

    def __update(self) -> None:
        self.config.clear()

        for section, options in self.items():
            self.config[section] = options

        with io.StringIO() as ss:
            self.config.write(ss)
            ss.seek(0)
            _ = self.connector.sudo_run(f"echo '{ss.read()}' > {self.path.absolute().__str__()}")
