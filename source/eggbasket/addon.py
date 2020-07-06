import mitmproxy.tcp

from mitmproxy import (
    proxy, options
)

from mitmproxy.tools.dump import (
    DumpMaster
)


from dataclasses import (
    dataclass, field
)

@dataclass
class License:
    host: str
    port: int
    local_port: int
    user: str = field(
        default='unknown'
    )
    
    def __eq__(self, other):
        return (
            self.host == other.host and
            self.port == other.port and
            self.local_port == other.local_port
        )

    def __hash__(self):
        return (
            hash((self.host, self.port, self.local_port))
        )


class BaseAddon:
    def __init__(self, license):
        self.license = license

    def _license_entry(self, host: str, port:int, local_port:int) -> License:
        return License(
            host, port, local_port
        )

    def clientconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        """
        A client has connected to mitmproxy. Note that a connection can
        correspond to multiple HTTP requests.
        """

        self.license.increment(
            self._license_entry(
                layer.ctx.client_conn.address[0], 
                layer.server_conn.address[1], 
                layer.ctx.client_conn.address[1]
            )
        )

    def clientdisconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        """
        A client has disconnected from mitmproxy.
        """

        self.license.decrement(
            self._license_entry(
                layer.ctx.client_conn.address[0], 
                layer.server_conn.address[1], 
                layer.ctx.client_conn.address[1]
            )
        )

    def tcp_error(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP error has occurred.
        """

        host, local_port = (
            flow.client_conn.address
        )                        

        self.license.decrement(
            self._license_entry(
                host, flow.server_conn.address[1], local_port
            )
        )
    
    def tcp_end(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has ended.
        """
        self.tcp_error(flow)  

    def tcp_message(self, flow: mitmproxy.tcp.TCPFlow):
        """
        A TCP connection has received a message. The most recent message
        will be flow.messages[-1]. The message is user-modifiable.
        """
        pass

