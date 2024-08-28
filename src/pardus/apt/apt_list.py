from logging import Logger, getLogger

from typing import List, Dict, Optional, Union, Iterator, Any
from typing_extensions import Self

from pardus import Apt
from pardus.apt.model_apt_list import ModelAptList
from pardus.connection.model_connector import ModelConnector
from pardus.utils.error import NumberOfElementsError


class AptList(ModelAptList):
    def __init__(self, apts: List[Apt], logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        if len(apts) == 0:
            raise NumberOfElementsError("apts can not be empty")

        self.apts = apts

    def __iter__(self) -> Iterator[Apt]:
        for x in self.apts:
            yield x

    def __getitem__(self, key: Union[int, slice]) -> Union[Apt, Self]:

        if isinstance(key, int):
            return self.apts[key]
        elif isinstance(key, slice):
            return self.__class__(self.apts[key])

        self.logger.error("Wrong slice")
        raise ValueError("Wrong slice")

    def __delitem__(self, key) -> None:
        del self.apts[key]

    def __len__(self) -> int:
        return len(self.apts)

    @classmethod
    def from_connections(cls, connections: List[ModelConnector], logger: Optional[Logger] = None) -> Self:
        return cls(
            [
                Apt(connection, logger=logger)
                for connection in connections
            ]
        )

    def repositories(self) -> Dict[Apt, List[Dict[str, str]]]:
        repositories = {}
        for apt in self.apts:
            try:
                repositories[apt] = apt.repositories()
            except Exception as e:
                self.logger.warning(e)

        return repositories

    def add_repository(self, repository: str) -> None:
        for apt in self.apts:
            try:
                apt.add_repository(repository)
            except Exception as e:
                self.logger.warning(e)

    def update(self) -> None:
        for apt in self.apts:
            try:
                apt.update()
            except Exception as e:
                self.logger.warning(e)

    def upgrade(self, package_name: Optional[str] = None) -> None:
        for apt in self.apts:
            try:
                apt.upgrade(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def list(self, installed: bool = False, upgradeable: bool = False) -> Dict[Apt, List[Dict[str, str]]]:
        list_of_available = {}
        for apt in self.apts:
            try:
                list_of_available[apt] = apt.list(installed=installed, upgradeable=upgradeable)
            except Exception as e:
                self.logger.warning(e)

        return list_of_available

    def install(self, package_name: Union[str, List[str]]) -> None:
        for apt in self.apts:
            try:
                apt.install(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def reinstall(self, package_name: Union[str, List[str]]) -> None:
        for apt in self.apts:
            try:
                apt.reinstall(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def remove(self, package_name: Union[str, List[str]]) -> None:
        for apt in self.apts:
            try:
                apt.remove(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def purge(self, package_name: Union[str, List[str]]) -> None:
        for apt in self.apts:
            try:
                apt.purge(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def search(self, package_name: str) -> Dict[Apt, List[Dict[str, str]]]:
        list_of_available = {}
        for apt in self.apts:
            try:
                list_of_available[apt] = apt.search(package_name)
            except Exception as e:
                self.logger.warning(e)

        return list_of_available

    def show(self, package_name: str) -> Dict[Apt, Dict[Union[str, None], Any]]:
        list_of_available = {}
        for apt in self.apts:
            try:
                list_of_available[apt] = apt.show(package_name)
            except Exception as e:
                self.logger.warning(e)

        return list_of_available
