from typing import Union
import requests, time

class ClientException(Exception):
    "Raised on errors from Banana client"
    def __init__(self, message = "" , res: requests.Response = None):
        if res != None:
            self.message = res.text
        else:
            self.message = message
        self.message = "\n" + self.message
        super().__init__(self.message)

class Client():
    def __init__(self, api_key, model_key, base_url):
        self.api_key = api_key
        self.model_key = model_key
        self.base_url = base_url

    def call(self, route: str, json: dict = {}, headers: dict = {}, use_replica: Union[str, None] = None, retry=True, retry_timeout = 300):
        headers["Content-Type"] = "application/json"
        headers['X-BANANA-API-KEY'] = self.api_key
        headers['X-BANANA-MODEL-KEY'] = self.model_key
        if use_replica != None:
            headers["X-USE-REPLICA"] = use_replica
        endpoint = self.base_url.rstrip("/") + "/" + route.lstrip("/")

        backoff_interval = 0.1 # seed for exponential backoff
        start = time.time()
        i = 0
        while True:
            if time.time() - start > retry_timeout:
                raise ClientException(message="Retry timeout exceeded")
            
            backoff_interval *= 2
            
            res = requests.post(endpoint, json=json, headers=headers)
            
            # success case -> return json
            if res.status_code == 200:
                meta = {"headers":res.headers}
                try:
                    return res.json(), meta
                except:
                    return {}, meta

            # user at their quota -> retry
            elif res.status_code == 400:
                if not retry:
                    raise ClientException(res=res)
                time.sleep(backoff_interval)
                continue
            
            # bad auth -> error
            elif res.status_code == 401:
                raise ClientException(res=res)

            # potassium endpoint doesn't exist -> error
            elif res.status_code == 404:
                raise ClientException(res=res)
            
            # payload too large -> error
            elif res.status_code == 413:
                raise ClientException(res=res)
            
            # banana is teapot -> error
            elif res.status_code == 418:
                raise ClientException("banana is a teapot")
            
            # potassium threw thread lock error -> retry
            elif res.status_code == 423:
                if not retry:
                    message = res.text
                    message += "423 errors are returned by Potassium when your server(s) are all busy handling GPU endpoints.\nIn most cases, you just want to retry later. Running banana.call() with the retry=True argument handles this for you."
                    raise ClientException(message=message)
                time.sleep(backoff_interval)
                continue
            
            # banana (or users server) had an unrecoverable error -> error
            elif res.status_code == 500:
                if not retry:
                    raise ClientException(res=res)
            
            # banana had a temporary error -> retry
            elif res.status_code == 503:
                if not retry:
                    raise ClientException(res=res)
                time.sleep(backoff_interval)
                continue

            else:
                raise ClientException(message="unexpected http response code: " + res.status_code)