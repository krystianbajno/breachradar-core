import importlib
import os
import yaml

class PluginLoader:
    def __init__(self, app, plugin_directory="plugins"):
        self.plugin_directory = plugin_directory
        self.app = app
        self.loaded_plugins = {
            'collectors': [],
            'processors': []
        }

    def load_plugins(self):
        """Load all plugins based on file names ('collector' or 'processor')."""
        for plugin_name in os.listdir(self.plugin_directory):
            plugin_path = os.path.join(self.plugin_directory, plugin_name)
            plugin_config_path = os.path.join(plugin_path, 'config', 'config.yaml')

            if os.path.isfile(plugin_config_path):
                with open(plugin_config_path, 'r') as config_file:
                    config = yaml.safe_load(config_file)
                    if config.get('enabled', False):
                        self._load_plugin(plugin_name)

    def _load_plugin(self, plugin_name):
        """Dynamically load plugin based on file names ('collector' or 'processor')."""
        plugin_path = os.path.join(self.plugin_directory, plugin_name)
        for root, _, files in os.walk(plugin_path):
            for file in files:
                if file.endswith("_collector.py"):
                    self._load_plugin_type(plugin_name, 'collector', root, file)
                elif file.endswith("_processor.py"):
                    self._load_plugin_type(plugin_name, 'processor', root, file)

    def _load_plugin_type(self, plugin_name, plugin_type, root, file):
        """Load the plugin type ('collector' or 'processor') and instantiate it."""
        try:
            module_rel_path = os.path.relpath(os.path.join(root, file), self.plugin_directory).replace(os.sep, ".").replace(".py", "")
            module_path = f"{self.plugin_directory}.{module_rel_path}"

            module = importlib.import_module(module_path)
                        
            class_name = ''.join([word.capitalize() for word in file.replace('.py', '').split('_')])

            plugin_class = getattr(module, class_name)
                        
            plugin_instance = plugin_class(self.app)

            self.loaded_plugins[f'{plugin_type}s'].append(plugin_instance)

            print(self.loaded_plugins)
        except (ImportError, AttributeError) as e:
            print(f"Failed to load {plugin_type} for plugin '{plugin_name}': {e}")

    def get_plugins(self, plugin_type):
        """Return all loaded plugins of a specific type (collector or processor)."""
        if plugin_type in ['collector', 'processor']:
            return self.loaded_plugins[f'{plugin_type}s']
        else:
            raise ValueError(f"Unsupported plugin type: {plugin_type}")
