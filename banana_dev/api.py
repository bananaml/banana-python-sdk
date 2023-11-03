from typing import Tuple
import requests


class API():
    "The Banana API class interacts with the Banana API."
    def __init__(self, api_key):
        self.base_url = "https://api.banana.dev/v1"
        self.api_key = api_key.strip()

    "Get all projects under the team account"
    def list_projects(self, query: dict = {}) -> Tuple[dict, int]:
        return self.__call("GET", "projects", query)

    "Get a specific project by ID"
    def get_project(self, project_id: str, query: dict = {}) -> Tuple[dict, int]:
        return self.__call("GET", f"projects/{project_id}", query)
    
    "Update a project's settings"
    def update_project(self, project_id: str, json: dict = {}) -> Tuple[dict, int]:
        return self.__call("PUT", f"projects/{project_id}", json)

    def __call(self, method: str, route: str, data: dict = {}) -> Tuple[dict, int]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-BANANA-API-KEY": self.api_key
        }

        endpoint = f"{self.base_url}/{route}"

        if method == "POST":
            res = requests.post(endpoint, json=data, headers=headers)
        elif method == "PUT":
            res = requests.put(endpoint, json=data, headers=headers)
        elif method == "GET":
            res = requests.get(endpoint, params=data, headers=headers)

        return res.json(), res.status_code
