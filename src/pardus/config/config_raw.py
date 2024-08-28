from logging import Logger, getLogger
from pathlib import Path
from typing import Union, Optional

from pardus.connection.model_connector import ModelConnector


class ConfigRaw:
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

        self.__data = self.read()

    def __str__(self) -> str:
        return self.data

    def __len__(self) -> int:
        return len(self.data)

    @property
    def data(self) -> str:
        return self.__data

    @data.setter
    def data(self, data) -> None:
        self.__data = data
        self.__update()

    def read(self) -> str:
        stdout = self.connector.sudo_run(f"cat {self.path.absolute().__str__()}", passwd=self.sudo_passwd)
        return str(stdout.read().decode())

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

    def touch(self) -> None:
        _ = self.connector.sudo_run(
            f"mkdir -p {self.path.parent.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = self.connector.sudo_run(f"touch {self.path.absolute().__str__()}", passwd=self.sudo_passwd)

    def __update(self) -> None:
        _ = self.connector.sudo_run(f"echo '{self.data}' > {self.path.absolute().__str__()}")