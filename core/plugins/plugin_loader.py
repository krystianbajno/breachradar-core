import importlib
import os
import yaml

class PluginLoader:
    def __init__(self, app, plugin_directory="./plugins"):
        self.plugin_directory = plugin_directory
        self.app = app

    def load_plugins(self, type):
        plugins = []
        for plugin_name in os.listdir(self.plugin_directory):
            plugin_path = os.path.join(self.plugin_directory, plugin_name, 'config', 'config.yaml')
            if os.path.isfile(plugin_path):
                with open(plugin_path, 'r') as config_file:
                    config = yaml.safe_load(config_file)
                    if config.get(type, {}).get('enabled'):
                        plugin = self._load_plugin(plugin_name, type)
                        if plugin:
                            plugins.append(plugin)
        return plugins

    def _load_plugin(self, plugin_name, type):
        try:
            module = importlib.import_module(f"plugins.{plugin_name}.{type}s.{plugin_name}_{type}")
            class_name = f"{plugin_name.capitalize()}{type.capitalize()}"
            plugin_class = getattr(module, class_name)

            return plugin_class(self.app)
        except ImportError as e:
            print(f"Failed to load plugin {plugin_name}: {str(e)}")
            return None
