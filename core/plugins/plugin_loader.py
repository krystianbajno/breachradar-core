import os
import importlib
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
        for plugin_name in os.listdir(self.plugin_directory):

            plugin_config_path = os.path.join(self.plugin_directory, plugin_name, 'config', 'config.yaml')

            if os.path.isfile(plugin_config_path):

                with open(plugin_config_path, 'r') as config_file:
                    plugin_config = yaml.safe_load(config_file)

                if not plugin_config.get('enabled', False):
                    print(f"Plugin '{plugin_name}' is disabled, skipping...")
                    continue

            plugin_provider_module = f"{self.plugin_directory}.{plugin_name}.providers.{plugin_name}_provider"
            
            try:
                provider_module = importlib.import_module(plugin_provider_module)

                provider_class_name = ''.join([word.capitalize() for word in plugin_name.split('_')]) + "Provider"
                provider_class = getattr(provider_module, provider_class_name)

                provider_instance = provider_class(self.app)
                provider_instance.register()

                self.loaded_plugins['collectors'].extend(provider_instance.get_collectors())
                self.loaded_plugins['processors'].extend(provider_instance.get_processors())

            except (ImportError, AttributeError) as e:
                print(f"Failed to load provider for plugin '{plugin_name}': {e}")

    def get_plugins(self, plugin_type):
        if plugin_type in ['collector', 'processor']:
            return self.loaded_plugins[f'{plugin_type}s']
        else:
            raise ValueError(f"Unsupported plugin type: {plugin_type}")
