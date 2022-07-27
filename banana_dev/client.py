import httpx
import time
from uuid import uuid4
from loguru import logger
from typing import Dict, Optional, Any, List, Union

from .models import BananaModel
from .configs import BananaConfig
from .utils import timer

class BananaClient:
    def __init__(
        self,
        apikey: Optional[str] = None,
        models: Optional[Dict[str, str]] = None,
        model_name: Optional[str] = None,
        model_key: Optional[str] = None,
        config_path: Optional[str] = None, 
        default_timeout: int = 30, 
        **kwargs
    ):
        """
        Initialize the Client with `httpx` and pass kwargs to `httpx.Client`
        """
        self.config = BananaConfig
        self.config_path = config_path
        self.default_timeout = default_timeout
        if config_path: 
            self.config.load_config(config_path)
        elif any([apikey, models, model_name, model_key]):
            if apikey: self.config.apikey = apikey
            if models: self.config.models = models
            if model_key: self.config.models[model_name or 'default'] = model_key
            if model_name and self.config.models.get(model_name): self.config.current_model = model_name
            elif self.config.models: self.config.current_model = list(self.config.models.keys())[0]
            self.config.save_config(self.config_path)
        
        self.models: Dict[str, BananaModel] = self.config.load_models()
        # Initialize a Sync Client and an Async Client
        self.client = httpx.Client(base_url = self.config.base_url, **kwargs)
        self.aclient = httpx.AsyncClient(base_url = self.config.base_url, **kwargs)

    

    # API Management Methods
    def call_api(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch results from a model
        """
        start_timer = timer()
        results = self.start_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)
        # if ignore errors is present, then it would return the response
        if not isinstance(results, dict): return None
        if results["finished"]: return self._return_results(results, duration = start_timer)
        while True:
            results = self.check_api(call_id = results["callID"], timeout = timeout, **kwargs)
            if not isinstance(results, dict): return None
            if results['message'].lower() == "success": 
                return self._return_results(results, duration = start_timer)


    def start_api(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Start an API call on the server
        """
        model = self.get_model(model_name)
        payload = {
            "id": str(uuid4()),
            "created": int(time.time()),
            "apiKey" : self.config.apikey,
            "modelKey" : model.key,
            "modelInputs" : model_inputs,
            "startOnly": start_only
        }
        response = self.client.post("start/v3/", json=payload, timeout = timeout or self.default_timeout, **kwargs)
        return self._validate_response(response, ignore_errors = ignore_errors)
    
    def check_api(self, call_id: str, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Check the status of an API call
        """
        payload = {
            "id": str(uuid4()),
            "created": int(time.time()),
            "longPoll": True,
            "callID": call_id, 
            "apiKey": self.config.apikey,
        }
        response = self.client.post("check/v3/", json = payload, timeout = timeout or self.default_timeout, **kwargs)
        return self._validate_response(response)
    
    # Async API Management Methods
    async def async_call_api(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch results from a model
        """
        start_timer = timer()
        results = await self.async_start_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)
        # if ignore errors is present, then it would return the response
        if not isinstance(results, dict): return None
        if results["finished"]: return self._return_results(results, duration = start_timer)
        while True:
            results = await self.async_check_api(call_id = results["callID"], timeout = timeout, **kwargs)
            if not isinstance(results, dict): return None
            if results['message'].lower() == "success": 
                return self._return_results(results, duration = start_timer)


    async def async_start_api(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Start an API call on the server
        """
        model = self.get_model(model_name)
        payload = {
            "id": str(uuid4()),
            "created": int(time.time()),
            "apiKey" : self.config.apikey,
            "modelKey" : model.key,
            "modelInputs" : model_inputs,
            "startOnly": start_only
        }
        response = await self.aclient.post("start/v3/", json=payload, timeout = timeout or self.default_timeout, **kwargs)
        return self._validate_response(response, ignore_errors = ignore_errors)
    
    async def async_check_api(self, call_id: str, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Check the status of an API call
        """
        payload = {
            "id": str(uuid4()),
            "created": int(time.time()),
            "longPoll": True,
            "callID": call_id, 
            "apiKey": self.config.apikey,
        }
        response = await self.aclient.post("check/v3/", json = payload, timeout = timeout or self.default_timeout, **kwargs)
        return self._validate_response(response)
    
    # Utility Methods
    def _return_results(self, results: Dict[str, Any], duration: Optional[float] = None) -> Dict[str, Any]:
        """
        Helper Method to return results
        """
        return  {
            "id": results["id"],
            "message": results["message"],
            "created": results["created"],
            "apiVersion": results["apiVersion"],
            "modelOutputs": results["modelOutputs"],
            "duration": timer(duration) if duration else None,
        }


    def _validate_response(self, response: httpx.Response, ignore_errors: bool = True):
        """
        Helper Method to validate the response
        """
        if response.status_code != 200:
            if not ignore_errors: raise httpx.RequestError(f"Server error: status code {response.status_code}")
            logger.error(f"Server error: status code {response.status_code}")
            return response
        try:
            out = response.json()
        except Exception as e:
            if not ignore_errors: raise ValueError(f"Server error: {e}") from e
            logger.error(f"Server error: {e}")
            return response

        if "error" in out['message'].lower():
            if not ignore_errors: raise ValueError(out['message'])
            logger.error(out['message'])
            return response
        return out

    # Model Management Methods
    def get_model(self, model_name: Optional[str] = None) -> BananaModel:
        """
        Return a model from the client's model list
        """
        return self.models.get(model_name or self.config.current_model)
    
    def add_model(self, model_name: str, model_key: str, set_as_current_model: bool = True, save_config: bool = True, config_path: Optional[str] = None):
        """
        Add a model to the client's model list
        """
        logger.info(f'Adding Model: {model_name}')
        self.config.models[model_name] = model_key
        self.models[model_name] = BananaModel(name = model_name, key = model_key)
        if set_as_current_model: 
            self.config.current_model = model_name
            logger.info(f'Setting Current Model to: {model_name}')
        if save_config: self.config.save_config(config_path or self.config_path)
    
    def remove_model(self, model_name: str, save_config: bool = True, config_path: Optional[str] = None):
        """
        Remove a model from client's model list

        If the model is the current model, set the current model to first model in the list
        """
        del self.config.models[model_name]
        del self.models[model_name]
        if self.config.current_model == model_name: 
            self.config.current_model = list(self.config.models.keys())[0]
            logger.info(f'Setting New Default Model to: {self.config.current_model}')
        if save_config: self.config.save_config(config_path or self.config_path)
    

    async def async_run(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Call the model with the given inputs
        """
        return await self.async_call_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)

    
    def run(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Call the model with the given inputs
        """
        return self.call_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)
    
    
    def __call__(self, model_inputs: Any, model_name: Optional[str] = None, start_only: bool = False, ignore_errors: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Call the model with the given inputs
        """
        return self.call_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)

class BananaLogs:
    config: BananaConfig = BananaConfig
    server_url: str = 'https://logs.banana.dev'
    log_results: Dict[str, Dict[Any, Any]] = {'builds': {}}

    @classmethod
    def get_params(cls):
        return {
            'headers': {'Content-Type': 'application/json'},
            'json': {'apiKey': cls.config.apikey},
        }

    # Base Methods

    @classmethod
    def fetch_logs(cls, ignore_errors: bool = True, **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch the logs from the server
        """
        response = httpx.Client().post(cls.server_url, **cls.get_params(), **kwargs)
        try:
            return response.json()
        except Exception as e:
            if not ignore_errors: raise ValueError(f"Server error: {e}") from e
            logger.error(f"Server error: {e}")
            return None
    
    @classmethod
    async def async_fetch_logs(cls, ignore_errors: bool = True, **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch the logs from the server
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(cls.server_url, **cls.get_params(), **kwargs)
        try:
            return response.json()
        except Exception as e:
            if not ignore_errors: raise ValueError(f"Server error: {e}") from e
            logger.error(f"Server error: {e}")
            return None
    
    @classmethod
    def get_logs(cls, limit: int = 10, ignore_errors: bool = True, _type: str = 'builds', **kwargs):
        """
        Get the logs from the server
        """
        logs = cls.fetch_logs(ignore_errors = ignore_errors, **kwargs)
        if logs is None: return None
        if logs.get(_type):
            cls.log_results[_type].update({build['ID']: build for build in logs[_type]})
        if _type != 'all':
            return logs[_type][:limit] if limit else logs.get(_type, [])
        return logs

    @classmethod
    async def async_get_logs(cls, limit: int = 10, ignore_errors: bool = True, _type: str = 'builds', **kwargs):
        """
        Get the logs from the server
        """
        logs = await cls.async_fetch_logs(ignore_errors = ignore_errors, **kwargs)
        if logs is None: return None
        if logs.get(_type):
            cls.log_results[_type].update({build['ID']: build for build in logs[_type]})
        if _type != 'all':
            return logs[_type][:limit] if limit else logs.get(_type, [])
        return logs

    @classmethod
    def display(cls, log_events: List[Dict[str, Any]], print_limit: int = None, **kwargs):
        """
        Display the logs
        """
        _print_id = 0
        if print_limit: log_events = reversed(log_events)
        for event in log_events:
            logger.info(f'{event["ID"]} - {event["name"]} - {event["timestamp"]} - {event["modelKey"]}')
            log_msg = event.get('logs')
            if log_msg:
                msgs = log_msg.split('\x1b')
                for msg in msgs:
                    logger.info(msg)
                    _print_id += 1
                    if print_limit and _print_id >= print_limit: 
                        break


    @classmethod
    def print_logs(cls, limit: int = 10, print_limit: int = 50, ignore_errors: bool = True, _type: str = 'builds', **kwargs):
        """
        Get the logs from the server
        """
        logs = cls.get_logs(limit = limit, ignore_errors = ignore_errors, _type = _type, **kwargs)
        if logs is None: return None
        for log in logs:
            log_events = log.get('events', [])
            cls.display(log_events, print_limit = print_limit)
            

    @classmethod
    async def async_print_logs(cls, limit: int = 10, print_limit: int = 50, ignore_errors: bool = True, _type: str = 'builds', **kwargs):
        """
        Get the logs from the server
        """
        logs = await cls.async_get_logs(limit = limit, ignore_errors = ignore_errors, _type = _type, **kwargs)
        if logs is None: return None
        for log in logs:
            log_events = log.get('events', [])
            cls.display(log_events, print_limit = print_limit)
            


## Compatibility Class 

class BananaRun:
    api: BananaClient = None

    @classmethod
    def init_api(
        cls, 
        apikey: Optional[str] = None,
        models: Optional[Dict[str, str]] = None,
        model_name: Optional[str] = None,
        model_key: Optional[str] = None,
        config_path: Optional[str] = None, 
        default_timeout: int = 30, 
        overwrite: bool = False,
        **kwargs
        ):
        """
        Initialize the API Client
        """
        if cls.api is None or overwrite:
            cls.api = BananaClient(
                apikey = apikey,
                models = models,
                model_name = model_name,
                model_key = model_key,
                config_path = config_path,
                default_timeout = default_timeout,
                **kwargs
            )

    @classmethod
    def run(
        cls, 
        model_inputs: Any, 
        model_name: Optional[str] = None, 
        start_only: bool = False, 
        ignore_errors: bool = False, 
        timeout: Optional[int] = None, 
        apikey: Optional[str] = None, 
        model_key: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        cls.init_api(model_name = model_name, model_key = model_key, apikey = apikey, overwrite = (apikey and model_key), **kwargs)
        return cls.api.run(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)
    
    @classmethod
    def start(
        cls, 
        model_inputs: Any, 
        model_name: Optional[str] = None, 
        start_only: bool = False, 
        ignore_errors: bool = False, 
        timeout: Optional[int] = None, 
        apikey: Optional[str] = None, 
        model_key: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        cls.init_api(model_name = model_name, model_key = model_key, apikey = apikey, overwrite = (apikey and model_key), **kwargs)
        return cls.api.start_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)


    @classmethod
    def check(
        cls, 
        call_id: str, 
        timeout: Optional[int] = None,
        model_name: Optional[str] = None,
        apikey: Optional[str] = None, 
        model_key: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        cls.init_api(model_name = model_name, model_key = model_key, apikey = apikey, overwrite = (apikey and model_key), **kwargs)
        return cls.api.check_api(call_id = call_id, timeout = timeout, **kwargs)

    @classmethod
    async def async_run(
        cls, 
        model_inputs: Any, 
        model_name: Optional[str] = None, 
        start_only: bool = False, 
        ignore_errors: bool = False, 
        timeout: Optional[int] = None, 
        apikey: Optional[str] = None, 
        model_key: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        cls.init_api(model_name = model_name, model_key = model_key, apikey = apikey, overwrite = (apikey and model_key), **kwargs)
        return await cls.api.async_run(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)
    
    @classmethod
    async def async_start(
        cls, 
        model_inputs: Any, 
        model_name: Optional[str] = None, 
        start_only: bool = False, 
        ignore_errors: bool = False, 
        timeout: Optional[int] = None, 
        apikey: Optional[str] = None, 
        model_key: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        cls.init_api(model_name = model_name, model_key = model_key, apikey = apikey, overwrite = (apikey and model_key), **kwargs)
        return await cls.api.async_start_api(model_inputs = model_inputs, model_name = model_name, start_only = start_only, ignore_errors = ignore_errors, timeout = timeout, **kwargs)


    @classmethod
    async def async_check(
        cls, 
        call_id: str, 
        timeout: Optional[int] = None,
        model_name: Optional[str] = None,
        apikey: Optional[str] = None, 
        model_key: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        cls.init_api(model_name = model_name, model_key = model_key, apikey = apikey, overwrite = (apikey and model_key), **kwargs)
        return await cls.api.async_check_api(call_id = call_id, timeout = timeout, **kwargs)

    