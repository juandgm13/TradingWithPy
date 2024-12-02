import json

class ConfigLoader:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.__load_config()

    def __load_config(self):
        """Private method to load the JSON configuration file."""
        try:
            with open(self.config_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found at {self.config_path}.")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON: {e}")

    def get(self, key, default=None):
        """Retrieve a configuration value."""
        return self.config.get(key, default)