import os
import yaml
from dotenv import load_dotenv
import logging

class Config:
    def __init__(self, env_file='.env', config_file='config.yaml'):
        load_dotenv(env_file)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        self.config_data = self._load_config_file(config_file)

    def _load_config_file(self, config_file):
        if not os.path.exists(config_file):
            self.logger.warning(f"Config file {config_file} not found, using environment variables only.")
            return {}

        try:
            with open(config_file, 'r') as file:
                self.logger.info(f"Loading config from {config_file}")
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config: {e}")
            return {}

    def get(self, key, default=None):
        value = os.getenv(key)
        if value is not None:
            return value
        
        keys = key.split('.')
        config_value = self.config_data
        try:
            for k in keys:
                config_value = config_value[k]
            return config_value
        except KeyError:
            self.logger.warning(f"Key {key} not found in config, using default {default}")
            return default

    def get_postgres_config(self):
        return {
            "database": self.get('POSTGRES_DB', 'cti_breach_hunter'),
            "user": self.get('POSTGRES_USER', 'cti_user'),
            "password": self.get('POSTGRES_PASSWORD', 'cti_password'),
            "host": self.get('POSTGRES_HOST', 'localhost'),
            "port": self.get('POSTGRES_PORT', '5432'),
        }

    def get_elasticsearch_config(self):
        return {
            "host": self.get('ELASTICSEARCH_HOST', 'localhost'),
            "port": self.get('ELASTICSEARCH_PORT', 9200),
        }
