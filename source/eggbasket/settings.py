import inspect
import typing
import logging
import dataclasses
from dataclasses import (
    dataclass, field
)

import json
import argparse

from eggbasket.base_plugin import (
    BasePlugin
)

from eggbasket.plugins import (
    create_plugin_from_settings
)


logger = logging.getLogger(
    __name__
)


class SettingsError(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

    @staticmethod
    def missing_property(name: str):
        return SettingsError("Property {} was not set.".format(name))


T = typing.TypeVar("T")


def load_dict_into_dataclass(
    dc: typing.Type[T], dict: typing.Mapping[str, typing.Any]
) -> T:
    props = {}

    fields = dataclasses.fields(dc)

    def process(tp, val):
        if dataclasses.is_dataclass(tp):
            val = load_dict_into_dataclass(tp, val)

        elif hasattr(tp, "_name") and tp._name == "Sequence":
            val = [process(tp.__args__[0], item) for item in val]

        return val

    for f in fields:
        if f.init is False:
            continue

        if f.name in dict:
            val = dict[f.name]
            val = process(f.type, val)
            props[f.name] = val
        else:
            if f.default is dataclasses.MISSING:
                raise SettingsError(
                    "Field {} is required (has no default).".format(f.name)
                )
            else:
                props[f.name] = f.default

    return dc(**props)


def _get_property(map: typing.Mapping[str, str], name: str) -> typing.Any:
    try:
        return map[name]
    except KeyError:
        raise SettingsError.missing_property(name)


@dataclass()
class Settings:
    licenses: typing.Sequence[typing.Any] = field(
        default_factory=lambda: []
    )

    @classmethod
    def load_dict(cls, data: typing.Mapping[str, typing.Any]):
        return load_dict_into_dataclass(Settings, data)

    def json(self):
        pass


def load_settings_json(json_str: str) -> Settings:
    data = json.loads(json_str)

    _plugins = data.pop(
        "licenses"
    )

    if not _plugins:
        raise RuntimeError("No plugins to .. sad panda")

    plugins = []
    for plugin in _plugins:
        plugins.append(
            create_plugin_from_settings(plugin)
        )

    data.setdefault(
        "licenses", plugins
    )

    settings = Settings.load_dict(data)

    return settings
