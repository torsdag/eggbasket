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
        class UniqueLicense(License):
            def __eq__(self, other):
                return (
                    self.host == other.host and
                    self.port == other.port
                )            

            def __hash__(self):
                return (
                    hash((self.host, self.port))
                )

        return (
            set([UniqueLicense(c.host, c.port, c.local_port, c.user) for c in self.clients])
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

        
