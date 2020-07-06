import struct
import typing
import logging
import mitmproxy.options

from dataclasses import (
    dataclass
)

from eggbasket.base_plugin import (
    BasePlugin
)

from eggbasket.addon import (
    BaseAddon
)

logger = logging.getLogger(
    __name__
)


@dataclass
class RLMSettings:
    name: str
    port: int
    port_isv: int
    hostname: str


class RLM(BasePlugin):
    def __init__(self, name:str, port:int, port_isv:int, hostname:str):
        self._name, self._port, self._port_isv, self._hostname = (
            name, port, port_isv, hostname
        )

        super().__init__()

    @property
    def options(self) -> [mitmproxy.options.Options]:
        proxie_options = list()
        for port in (self._port, self._port_isv):
            proxie_options.append(
                mitmproxy.options.Options(
                    mode='upstream:{0}:{1}'.format(  
                       self._hostname, port
                    ),
                    rawtcp=True, listen_port=port, ignore_hosts=['.*'], ssl_insecure=True,
                )
            )

        return (
            proxie_options
        )
        
    @property
    def addons(self) -> [BaseAddon]:
        port_isv = (
            self._port_isv
        )

        class RLMAddon(BaseAddon):
            def clientconnect(self, layer: mitmproxy.proxy.protocol.Layer):
                """
                A client has disconnected from mitmproxy.
                """
                if layer.server_conn.address[1] == port_isv:
                    super().clientconnect(layer)

            def clientdisconnect(self, layer: mitmproxy.proxy.protocol.Layer):
                """
                A client has disconnected from mitmproxy.
                """

                if layer.server_conn.address[1] == port_isv:
                    super().clientdisconnect(layer)

            def tcp_message(self, flow: mitmproxy.tcp.TCPFlow):
                raw_data = (
                    flow.messages[-1]
                ).content

                try:
                    # try to unpack the data to determine the user,
                    # only bother with the "intial" connection message.

                    header = (
                        struct.unpack(
                            '>bH3b', raw_data[:6]
                        )
                    )

                    data = (
                        struct.unpack(
                            '{0}s'.format(header[1]), raw_data[6:]
                        )
                    )

                    parsed_data = (
                        [ part for part in data[-1].decode('utf-8').split('\x00') if part ] 
                    )

                    host, _ = (
                        flow.client_conn.address
                    )            

                    for client in self.license.clients:
                        if not (
                            client.host == host and 
                            client.port == flow.server_conn.address[1]
                        ):
                            continue

                        client.user = (
                            parsed_data[3] # set username.
                        )

                except (struct.error, UnicodeDecodeError) as error:
                    # dirty panda, but yeah only care about the first
                    # message..
                    logger.debug(
                        'Failed to parse message {} due to {}'.format(
                            raw_data, error
                        )
                    )
                except IndexError as error:
                    # 
                    logger.debug(
                        'Failed to parse message {} due to {}'.format(
                            raw_data, error
                        )
                    )
        return [
            RLMAddon(self),
        ]

    @classmethod
    def create_from_dict(cls, data: typing.Mapping[str, typing.Any]) -> BasePlugin:
        from eggbasket.settings import (
            load_dict_into_dataclass
        )

        settings = load_dict_into_dataclass(
            RLMSettings, data
        )

        return cls(
            settings.name, settings.port, settings.port_isv, settings.hostname
        )
