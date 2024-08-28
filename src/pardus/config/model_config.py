from abc import ABC, abstractmethod
from typing import Dict


class ModelConfig(ABC):
    @abstractmethod
    def __setitem__(self, key: str, value: Dict[str, str]) -> None:
        """Updates the dict on add/update to representing the config file"""

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        """Updates the dict on delete to representing the config file"""

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Updates the dict on update method to representing the config file"""
