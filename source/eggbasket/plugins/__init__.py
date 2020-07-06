import logging
import pkg_resources
import pkgutil
import os
import importlib
import inspect

from eggbasket.base_plugin import (
    BasePlugin
)


logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Raised in response to errors reading Settings."""

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

    @staticmethod
    def invalid_plugin_type(type_name):
        return PluginError('Invalid plugin type: "{}"'.format(type_name))


def get_discovered_plugin_modules():
    """Find modules that have defined their entrypoint as interstate_love_song.plugins"""
    return {
        plugin.name: importlib.import_module("{0}.{1}".format(__name__, plugin.name))
        for plugin in pkgutil.iter_modules(__path__)
    }


def get_available_plugins():
    plugins = {}
    for _, module in get_discovered_plugin_modules().items():
        members = inspect.getmembers(
            module,
            lambda _m: inspect.isclass(_m)
            and _m is not BasePlugin
            and issubclass(_m, BasePlugin),
        )

        plugins.update(members)

        logger.info(
            "Plugins found : {0:10s} from {1}".format(
                ", ".join([m[0] for m in members]), module.__file__
            )
        )

    return plugins


def create_plugin_from_settings(settings):
    from ..settings import SettingsError

    try:
        plugin_type_name = settings["plugin"]

    except KeyError:
        raise PluginError("No plugin defined in mapper settings.")

    plugins = get_available_plugins()

    try:
        plugin_type = plugins[plugin_type_name]
        plugin_settings = settings.get(
            "settings", {}
        )

    except KeyError:
        raise PluginError.invalid_plugin_type(plugin_type_name)

    try:
        return plugin_type.create_from_dict(
            plugin_settings
        )
        
    except SettingsError as e:
        logger.error("Failed to configure plugin: {0}, {1}".format(plugin_type_name, e))

    raise PluginError("Couldn't create plugin from settings: {0}".format(settings))
