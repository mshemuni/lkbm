from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger

from typing import List, Dict, Union, Optional

from typing_extensions import Self

from pardus.connection.model_connector import ModelConnector


class ModelService(ABC):

    @abstractmethod
    def list(self) -> List[Dict[str, str]]:
        """Lists all services"""

    @abstractmethod
    def start(self, service: str) -> None:
        """Activates a service"""

    @abstractmethod
    def stop(self, service: str) -> None:
        """Stops a service"""

    @abstractmethod
    def restart(self, service: str) -> None:
        """Restarts a service"""

    @abstractmethod
    def enable(self, service: str) -> None:
        """Enables a service"""

    @abstractmethod
    def disable(self, service: str) -> None:
        """Disables a service"""

    @abstractmethod
    def logs(self, service) -> List[Dict[str, Union[str, datetime]]]:
        """Retrieves logs of a service"""
