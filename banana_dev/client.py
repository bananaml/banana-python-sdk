from typing import Union
import requests, time

class Client():
    def __init__(self, api_key, model_key, base_url):
        self.api_key = api_key
        self.model_key = model_key
        self.base_url = base_url

    def call(self, route: str, json: dict = {}, headers: dict = {}, use_replica: Union[str, None] = None, retry_timeout = 300):
        headers["Content-Type"] = "application/json"
        headers['X-BANANA-API-KEY'] = self.api_key
        headers['X-BANANA-MODEL-KEY'] = self.model_key
        if use_replica != None:
            headers["X-USE-REPLICA"] = use_replica
        endpoint = self.base_url.rstrip("/") + "/" + route.lstrip("/")

        backoff_interval = 0.1 # seed for exponential backoff
        start = time.time()
        while True:
            if time.time() - start > retry_timeout:
                raise "call timed out"
            
            backoff_interval *= 2
            
            res = requests.post(endpoint, json=json, headers=headers)

            # success case -> return json
            if res.status_code == 200:
                return res.json(), {"headers":res.headers}
            
            # user at their quota -> retry
            elif res.status_code == 400:
                time.sleep(backoff_interval)
                continue
            
            # bad auth -> error
            elif res.status_code == 401:
                print(res.content)
                raise "authorization failed"
            
            # potassium endpoint doesn't exist -> error
            elif res.status_code == 404:
                print(res.content)
                raise "potassium server returned 404"
            
            # payload too large -> error
            elif res.status_code == 413:
                print(res.content)
                raise "payload too large"
            
            # banana is teapot -> error
            elif res.status_code == 418:
                raise "banana is a teapot"
            
            # potassium threw thread lock error -> retry
            elif res.status_code == 423:
                time.sleep(backoff_interval)
                continue
            
            # banana (or users server) had an unrecoverable error -> error
            elif res.status_code == 500:
                print(res.content)
                raise "internal error"
            
            # banana had a temporary error -> retry
            elif res.status_code == 503:
                time.sleep(backoff_interval)
                continue

            else:
                print(res.content)
                raise "unexpected http response"