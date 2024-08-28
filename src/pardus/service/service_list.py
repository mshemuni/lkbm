from datetime import datetime
from logging import Logger, getLogger
from typing import List, Optional, Iterator, Union, Dict

from typing_extensions import Self

from pardus import Service
from pardus.connection.model_connector import ModelConnector
from pardus.service.model_service_list import ModelServiceList
from pardus.utils.error import NumberOfElementsError


class ServiceList(ModelServiceList):
    def __init__(self, services: List[Service], logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = getLogger(__name__)
        else:
            self.logger = logger

        if len(services) == 0:
            NumberOfElementsError("services can not be empty")

        self.services = services

    def __iter__(self) -> Iterator[Service]:
        for x in self.services:
            yield x

    def __getitem__(self, key: Union[int, slice]) -> Union[Service, Self]:

        if isinstance(key, int):
            return self.services[key]
        elif isinstance(key, slice):
            return self.__class__(self.services[key])

        self.logger.error("Wrong slice")
        raise ValueError("Wrong slice")

    def __delitem__(self, key) -> None:
        del self.services[key]

    def __len__(self) -> int:
        return len(self.services)

    @classmethod
    def from_connections(cls, connections: List[ModelConnector], logger: Optional[Logger] = None) -> Self:

        return cls(
            [
                Service(connection, logger=logger)
                for connection in connections
            ]
        )

    def list(self) -> Dict[Service, List[Dict[str, str]]]:
        lists = {}
        for each_service in self.services:
            try:
                lists[each_service] = each_service.list()
            except Exception as e:
                self.logger.error(e)
        return lists

    def activate(self, service: str) -> None:

        for each_service in self.services:
            try:
                each_service.activate(service)
            except Exception as e:
                self.logger.error(e)

    def stop(self, service: str) -> None:

        for each_service in self.services:
            try:
                each_service.stop(service)
            except Exception as e:
                self.logger.error(e)

    def restart(self, service: str) -> None:

        for each_service in self.services:
            try:
                each_service.restart(service)
            except Exception as e:
                self.logger.error(e)

    def enable(self, service: str) -> None:

        for each_service in self.services:
            try:
                each_service.enable(service)
            except Exception as e:
                self.logger.error(e)

    def disable(self, service: str) -> None:

        for each_service in self.services:
            try:
                each_service.disable(service)
            except Exception as e:
                self.logger.error(e)

    def logs(self, service) -> dict[Service, List[dict[str, str | datetime]]]:
        lists = {}
        for each_service in self.services:
            try:
                lists[each_service] = each_service.logs(service)
            except Exception as e:
                self.logger.error(e)
        return lists
