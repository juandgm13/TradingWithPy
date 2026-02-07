import pytest
import json
import os
import tempfile
from app.utils.config.config_loader import ConfigLoader


@pytest.fixture
def valid_config_file():
    """Create a temporary valid config file"""
    config_data = {
        "num_candles": 100,
        "indicators_period": 14,
        "timer_interval_ms": 5000,
        "enable_test_trading": True,
        "email_notifications": False,
        "email": {
            "sender": "test@example.com",
            "password": "test_password",
            "recipient": "recipient@example.com"
        }
    }

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def invalid_json_file():
    """Create a temporary file with invalid JSON"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json content }")
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def empty_config_file():
    """Create a temporary empty config file"""
    config_data = {}

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


class TestConfigLoaderInitialization:
    """Tests for ConfigLoader initialization"""

    def test_load_valid_config(self, valid_config_file):
        """Should load valid config file successfully"""
        config = ConfigLoader(valid_config_file)

        assert config.config is not None
        assert isinstance(config.config, dict)
        assert config.config["num_candles"] == 100
        assert config.config["indicators_period"] == 14

    def test_load_missing_file(self):
        """Should raise exception when config file doesn't exist"""
        non_existent_path = "/path/to/non/existent/config.json"

        with pytest.raises(Exception, match="Configuration file not found"):
            ConfigLoader(non_existent_path)

    def test_load_invalid_json(self, invalid_json_file):
        """Should raise exception when JSON is malformed"""
        with pytest.raises(Exception, match="Failed to parse JSON"):
            ConfigLoader(invalid_json_file)

    def test_load_empty_config(self, empty_config_file):
        """Should load empty config successfully"""
        config = ConfigLoader(empty_config_file)

        assert config.config is not None
        assert isinstance(config.config, dict)
        assert len(config.config) == 0


class TestConfigLoaderGet:
    """Tests for ConfigLoader.get() method"""

    def test_get_existing_key(self, valid_config_file):
        """Should return value for existing key"""
        config = ConfigLoader(valid_config_file)

        assert config.get("num_candles") == 100
        assert config.get("indicators_period") == 14
        assert config.get("enable_test_trading") is True
        assert config.get("email_notifications") is False

    def test_get_nested_key(self, valid_config_file):
        """Should return nested dictionary for nested key"""
        config = ConfigLoader(valid_config_file)

        email_config = config.get("email")
        assert isinstance(email_config, dict)
        assert email_config["sender"] == "test@example.com"
        assert email_config["password"] == "test_password"

    def test_get_missing_key_with_default(self, valid_config_file):
        """Should return default value when key doesn't exist"""
        config = ConfigLoader(valid_config_file)

        result = config.get("non_existent_key", "default_value")
        assert result == "default_value"

        result = config.get("missing_number", 42)
        assert result == 42

        result = config.get("missing_bool", False)
        assert result is False

    def test_get_missing_key_without_default(self, valid_config_file):
        """Should return None when key doesn't exist and no default provided"""
        config = ConfigLoader(valid_config_file)

        result = config.get("non_existent_key")
        assert result is None

    def test_get_from_empty_config(self, empty_config_file):
        """Should return default or None for empty config"""
        config = ConfigLoader(empty_config_file)

        assert config.get("any_key") is None
        assert config.get("any_key", "default") == "default"


class TestConfigLoaderDataTypes:
    """Tests for different data types in config"""

    def test_get_integer_values(self, valid_config_file):
        """Should correctly return integer values"""
        config = ConfigLoader(valid_config_file)

        num_candles = config.get("num_candles")
        assert isinstance(num_candles, int)
        assert num_candles == 100

    def test_get_boolean_values(self, valid_config_file):
        """Should correctly return boolean values"""
        config = ConfigLoader(valid_config_file)

        test_trading = config.get("enable_test_trading")
        assert isinstance(test_trading, bool)
        assert test_trading is True

        email_notif = config.get("email_notifications")
        assert isinstance(email_notif, bool)
        assert email_notif is False

    def test_get_string_values(self, valid_config_file):
        """Should correctly return string values"""
        config = ConfigLoader(valid_config_file)

        email_config = config.get("email")
        sender = email_config["sender"]
        assert isinstance(sender, str)
        assert sender == "test@example.com"

    def test_get_dict_values(self, valid_config_file):
        """Should correctly return dictionary values"""
        config = ConfigLoader(valid_config_file)

        email_config = config.get("email")
        assert isinstance(email_config, dict)
        assert "sender" in email_config
        assert "password" in email_config
        assert "recipient" in email_config


class TestConfigLoaderEdgeCases:
    """Tests for edge cases"""

    def test_config_with_special_characters(self):
        """Should handle config with special characters"""
        config_data = {
            "special_key": "value with spaces",
            "unicode_key": "café ñoño",
            "symbols": "!@#$%^&*()"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = ConfigLoader(temp_path)
            assert config.get("special_key") == "value with spaces"
            assert config.get("unicode_key") == "café ñoño"
            assert config.get("symbols") == "!@#$%^&*()"
        finally:
            os.unlink(temp_path)

    def test_config_with_null_values(self):
        """Should handle null values in config"""
        config_data = {
            "null_value": None,
            "empty_string": "",
            "zero": 0
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = ConfigLoader(temp_path)
            assert config.get("null_value") is None
            assert config.get("empty_string") == ""
            assert config.get("zero") == 0
        finally:
            os.unlink(temp_path)

    def test_config_with_list_values(self):
        """Should handle list values in config"""
        config_data = {
            "exchanges": ["binance", "alpaca"],
            "intervals": ["1h", "4h", "1d"],
            "numbers": [1, 2, 3, 4, 5]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = ConfigLoader(temp_path)
            exchanges = config.get("exchanges")
            assert isinstance(exchanges, list)
            assert exchanges == ["binance", "alpaca"]

            intervals = config.get("intervals")
            assert isinstance(intervals, list)
            assert len(intervals) == 3
        finally:
            os.unlink(temp_path)

    def test_config_path_stored(self, valid_config_file):
        """Should store config path for reference"""
        config = ConfigLoader(valid_config_file)

        assert config.config_path == valid_config_file

    def test_multiple_config_instances(self, valid_config_file):
        """Should allow multiple independent ConfigLoader instances"""
        config1 = ConfigLoader(valid_config_file)
        config2 = ConfigLoader(valid_config_file)

        assert config1.get("num_candles") == config2.get("num_candles")
        # They should be independent instances
        assert config1 is not config2


class TestConfigLoaderWithRealConfigStructure:
    """Tests using structure similar to actual config.json"""

    def test_real_world_config_structure(self):
        """Should work with realistic config structure"""
        config_data = {
            "num_candles": 100,
            "indicators_period": 14,
            "timer_interval_ms": 5000,
            "enable_test_trading": True,
            "email_notifications": False,
            "email": {
                "sender": "trading_bot@gmail.com",
                "password": "app_specific_password",
                "recipient": "user@example.com"
            },
            "strategies": {
                "three_screen": {
                    "enabled": True,
                    "long_interval": "1d",
                    "mid_interval": "4h",
                    "short_interval": "1h"
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = ConfigLoader(temp_path)

            # Test basic values
            assert config.get("num_candles", 50) == 100
            assert config.get("indicators_period", 10) == 14

            # Test with defaults that shouldn't be used
            assert config.get("enable_test_trading", False) is True

            # Test nested structures
            email = config.get("email", {})
            assert email["sender"] == "trading_bot@gmail.com"

            strategies = config.get("strategies", {})
            assert "three_screen" in strategies
            assert strategies["three_screen"]["enabled"] is True

            # Test missing keys with defaults
            assert config.get("missing_config", "default") == "default"

        finally:
            os.unlink(temp_path)
