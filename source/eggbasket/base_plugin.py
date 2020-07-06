import logging
import typing

from dataclasses import (
    dataclass
)

from abc import (
    ABC, abstractmethod
)

from eggbasket.addon import (
    License,
    BaseAddon
)


class BasePlugin(ABC):
    def __init__(self):
        self._clients = list()

    @property
    @abstractmethod
    def options(self):
        pass
    
    @property
    def name(self) -> str:
        return '{0}'.format(
            self._name
        )

    @property
    def addons(self) -> [BaseAddon]:
        return [
            BaseAddon(self),
        ]

    @property
    def clients(self) -> typing.Sequence[License]:
        return (
            self._clients
        )

    @property
    def licenses(self) -> typing.Sequence[License]:
        return (
            set(self.clients)
        )

    def decrement(self, data):
        if data in self._clients:
            self._clients.remove(
                data
            )

    def increment(self, data):
        self._clients.append(
            data
        )        

        
