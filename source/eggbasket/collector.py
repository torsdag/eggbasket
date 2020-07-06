import typing

from prometheus_client.core import (
    CounterMetricFamily,
    StateSetMetricFamily,
)

class LicenseCollector: 
    def __init__(self, licenses: typing.Sequence[typing.Any]):
        self._licenses = (
            licenses
        )

    def collect(self):
        license_counter =  CounterMetricFamily(
            "active_licenses", "active license count", labels=("license", )
        )

        client_state = StateSetMetricFamily(
            "active_licenses", "active license count", labels=("host", "port", "license", "user")
        )        
        for license in self._licenses:
            license_counter.add_metric(
                [license.name], len(license.licenses)
            )

            for client in license.licenses:
                client_state.add_metric(
                    (client.host, str(client.port), license.name, client.user), value={"active": True}
                )

        yield (
            license_counter
        )

        yield (
            client_state
        )




