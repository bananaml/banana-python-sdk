import os
import json
from pathlib import Path

from typing import Dict, Optional, Any
from loguru import logger
from .models import BananaModel

# Stores the Configuration for the Banana SDK
_config_path = Path.home().joinpath('.banana')
_config_path.mkdir(parents=True, exist_ok=True)
_config_file = _config_path.joinpath('config.json')
_config_data = json.loads(_config_file.read_text()) if _config_file.exists() else {}

# Allow for environment variables to overwrite config
class BananaConfig:
    apikey: Optional[str] = os.getenv('BANANA_APIKEY', _config_data.get('apikey', None))
    base_url: str = os.getenv('BANANA_URL', _config_data.get('url', 'https://api.banana.dev'))
    current_model: Optional[str] = os.getenv('BANANA_MODEL', _config_data.get('current_model', None))
    model_key: Optional[str] = os.getenv('BANANA_MODEL_KEY')
    models: Dict[str, str] = _config_data.get('models', {})

    @classmethod
    def load_config(cls, config_path: str):
        """
        Load BananaConfig from a JSON File

        default path: ~/.banana/config.json
        """
        config_file = Path(config_path)
        assert config_file.exists(), f'Config file: {config_path} does not exist'
        logger.info(f'Loading config from: {config_path}')
        config_data: Dict[str, Any] = json.loads(config_file.read_text())
        cls.apikey = config_data.get('apikey', cls.apikey)
        cls.base_url = config_data.get('url', cls.base_url)
        cls.current_model = config_data.get('current_model', cls.current_model)
        cls.models = config_data.get('models', cls.models)
        # if no current model, set to first model
        if not cls.current_model and cls.models:
            cls.current_model = list(cls.models.keys())[0]
            logger.info(f'Setting Current Model to: {cls.current_model}')
        cls.model_key = cls.models.get(cls.current_model, cls.model_key)
    
    @classmethod
    def save_config(cls, config_path: Optional[str] = None):
        """
        Save BananaConfig to a JSON File
        
        default path: ~/.banana/config.json
        """
        # if no config path, use default
        config_file = Path(config_path) if config_path else _config_file
        config_data = {
            'apikey': cls.apikey,
            'url': cls.base_url,
            'current_model': cls.current_model,
            'models': cls.models
        }
        config_file.write_text(json.dumps(config_data, indent=4))
        logger.info(f'Saved config to: {config_file}')
        return config_file
    
    @classmethod
    def load_models(cls) -> Dict[str, BananaModel]:
        """
        Load all models from Banana
        """
        return {model_name: BananaModel(name = model_name, key = model_key) for model_name, model_key in cls.models.items()}
    
    @classmethod
    def get_model_key(cls, model_name: Optional[str] = None):
        """
        Return the model key for a given model name

        If no model name is provided, return the current model key
        """
        return cls.models.get(model_name or cls.current_model, cls.model_key)









    


