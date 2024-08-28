from logging import Logger, getLogger
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from typing_extensions import Self

from pardus import Config
from pardus.config.model_config_list import ModelConfigList
from pardus.connection.model_connector import ModelConnector
from pardus.utils.error import NumberOfElementsError


class ConfigList(dict[Any, Any], ModelConfigList):
    def __init__(self, configs: List[Config], logger: Optional[Logger] = None):
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        if len(configs) == 0:
            raise NumberOfElementsError("configs can not be empty")

        self.configs = configs

        for each in self.configs:
            each.create_backup()
            each.clear()

        super().__init__({})

    def __setitem__(self, key: str, value: Dict["str", "str"]) -> None:
        super().__setitem__(key, value)
        for each in self.configs:
            each[key] = value

    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        for each in self.configs:
            del each[key]

    @classmethod
    def from_connections(cls, connections: List[ModelConnector],
                         files: Union[Union[str, Path], List[Union[str, Path]]],
                         sudo_passwds: Optional[Union[str, List[str]]] = None,
                         logger: Optional[Logger] = None) -> Self:

        if isinstance(files, list):
            files_to_use = files
        else:
            files_to_use = [files] * len(connections)

        sudo_passwds_to_use: Union[List[str], List[None], List[Union[str, None]]]

        if isinstance(sudo_passwds, list):
            sudo_passwds_to_use = sudo_passwds
        else:
            sudo_passwds_to_use = [sudo_passwds] * len(connections)

        return cls(
            [
                Config(connection, file,create=True, backup=True, force=True, sudo_passwd=sudo_passwd, logger=logger)
                for connection, file, sudo_passwd in zip(connections, files_to_use, sudo_passwds_to_use)
            ]
        )

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        for each in self.configs:
            each.update(*args, **kwargs)

    def length(self) -> int:
        return len(self.configs)

    def take_element(self, index: int) -> None:
        del self.configs[index]

    def get_element(self, key: Union[int, slice]) -> Union[Config, Self]:
        if isinstance(key, int):
            return self.configs[key]
        elif isinstance(key, slice):
            return self.__class__(self.configs[key])

    def clear(self) -> None:
        for config in self.configs:
            try:
                config.clear()
            except Exception as e:
                self.logger.error(e)
