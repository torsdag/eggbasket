import sys
import time
import mock
import typing
import logging
import argparse

from prometheus_client import (
    start_http_server, 
    Summary, 
    CollectorRegistry, 
    REGISTRY
)

from eggbasket.collector import (
    LicenseCollector
)

logger = logging.getLogger(
    __name__
)


def monkey_patch_mitm_tcp_layer():
    """
    Patch the raw tcp layer to not ignore the events.
    dirty hobbit.
    """

    import mitmproxy.proxy.protocol.rawtcp
    
    old_init = (
        mitmproxy.proxy.protocol.rawtcp.RawTCPLayer.__init__
    )
    def new_init(self, ctx, ignore=False):
        self.ignore = False
        old_init(self, ctx)     
    
    mitmproxy.proxy.protocol.rawtcp.RawTCPLayer.__init__ = (
        new_init
    )
    

def main():
    parser = argparse.ArgumentParser("eggbasket")

    parser.add_argument(
        "-c", "--config", required=True, help=("json config file.")
    )

    parser.add_argument(
        "-p", "--port", default=8000, help=("port for prometheus exporter")
    )

    parser.add_argument(
        "-v", "--verbose", help=("verbose logging"), action="store_true"
    )

    args = parser.parse_args()

    from eggbasket.settings import (
        load_settings_json
    )

    try:
        settings = load_settings_json(
            open(args.config, "r"
        ).read())

    except FileNotFoundError as error:
        raise

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    # Cant for the life of me figure out how to
    # make the tcp layer work, super dirty monkey
    # patch to enable the events... bad panda
    monkey_patch_mitm_tcp_layer()

    from eggbasket.proxy import Proxy

    proxies = []
    for license in settings.licenses:
        proxies.extend(
            [
                (Proxy(license, options, license.addons), time.sleep(0.5))[0]
                for options in license.options
            ]
        )

        logger.info(
            "Started proxy for license: {0}@{1}".format(
                license.name, license.__class__.__name__
            ),
        )

    registry = CollectorRegistry()

    REGISTRY.register(
        LicenseCollector(settings.licenses)
    )

    start_http_server(args.port)

    try:
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        for proxy in proxies:
            proxy.stop()

    logger.info("Done.")


if __name__ == "__main__":
    main()
