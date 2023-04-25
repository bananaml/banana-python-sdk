from typing import Union
import requests

class Client():
    def __init__(self, api_key, model_key, base_url):
        self.api_key = api_key
        self.model_key = model_key
        self.base_url = base_url

    def call(self, route: str, json: dict = {}, headers: dict = {}, use_replica: Union[str, None] = None):
        headers["Content-Type"] = "application/json"
        headers['X-BANANA-API-KEY'] = self.api_key
        headers['X-BANANA-MODEL-KEY'] = self.model_key
        if use_replica != None:
            headers["X-USE-REPLICA"] = use_replica

        print(headers)

        endpoint = self.base_url.rstrip("/") + "/" + route.lstrip("/")
        print(endpoint)

        res = requests.post(endpoint, json=json, headers=headers)
        print(res.content)