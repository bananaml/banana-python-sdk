from typing import Union, Tuple
import requests

API_BASE_URL = "https://api.banana.dev/v1"


class API():
    "The Banana API class interacts with the Banana API."
    def __init__(self, api_key):
        self.api_key = api_key

    "Get the projects API client"
    def projects(self) -> "ProjectsAPI":
        return ProjectsAPI(self.api_key)


class ProjectsAPI():
    "The Banana Projects API class is for interacting with Banana's API for project automation."
    def __init__(self, api_key,):
        self.api_key = api_key

    "Get all projects under the team account"
    def list(self, route: str, json: dict = {}) -> Tuple[dict, dict]:
        return self.__call("GET", route, json)

    "Get a specific project by ID"
    def get(self, project_id: str) -> Tuple[dict, dict]:
        return self.__call("GET", f"projects/{project_id}")
    
    "Update a project's settings"
    def update(self, project_id: str, json: dict = {}) -> Tuple[dict, dict]:
        return self.__call("PUT", f"projects/{project_id}", json)

    def __call(self, method: str, route: str, data: dict = {}) -> Tuple[dict, dict]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-BANANA-API-KEY": self.api_key
        }

        endpoint = f"{API_BASE_URL}/{route}"

        if method == "POST":
            res = requests.post(endpoint, json=data, headers=headers)
        elif method == "GET":
            res = requests.get(endpoint, headers=headers)

        meta = {"headers":res.headers}
        try:
            return res.json(), meta
        except:
            return {}, meta
