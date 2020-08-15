
import os
import importlib


class Plugins:

    def __init__(self, plugins_dir: str):
        self._plugin_dir = plugins_dir
        self._loads = set()
        self._not_loads = set()

    def auto_load_plugins(self) -> None:
        plugins = [i for i in os.listdir(self._plugin_dir)
                   if os.path.isdir(f'{self._plugin_dir}/{i}')]
        for plugin in plugins:
            if plugin in self._not_loads:
                continue
            module = importlib.import_module(
                '{}.{}'.format(self._plugin_dir, plugin))
            self._loads.add(module.__name__)

    def load_plugins(self, module_name: str) -> None:
        module = importlib.import_module(
            '{}.{}'.format(self._plugin_dir, module_name))
        self._loads.add(module.__name__)

    def not_load_plugins(self, module_name: str) -> None:
        self._not_loads.add(module_name)

    @property
    def plugins_info(self) -> set:
        return self._loads
