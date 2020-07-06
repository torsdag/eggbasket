import asyncio
import typing
import logging
import threading

from mitmproxy import (
    proxy, options
)

from mitmproxy.tools.dump import (
    DumpMaster
)

from eggbasket.addon import(
    BaseAddon
)

logger = logging.getLogger(
    __name__
)

class Proxy(threading.Thread):
    def __init__(
        self, license, options: options.Options, addons: typing.Sequence[BaseAddon]
    ):
        super(Proxy, self).__init__(
            None, None, None
        )
        self._license, self._options, self._addons = (
            license, options, addons
        )

        self.start()

    def run(self):
        loop = asyncio.new_event_loop()
        
        asyncio.set_event_loop(
            loop
        )

        p_conf = proxy.config.ProxyConfig(
            self._options
        )

        self._master = (
            DumpMaster(None)
        )

        self._master.server = (
            proxy.server.ProxyServer(p_conf)
        )

        self._master.addons.get('core').load(
            self._options
        )

        for addon in self._addons:
            self._master.addons.add(
                addon
            )

        self._master.run(loop)

    def stop(self):
        self._master.shutdown()

        logger.info(
            'Shutting down proxy on port: {}'.format(
                self._options.listen_port
            )
        )