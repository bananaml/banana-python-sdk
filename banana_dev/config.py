import os
import json
from uuid import uuid4

def load_config():
    user_path = os.path.expanduser("~")
    cache_path = os.path.join(user_path, ".banana")
    config_path = os.path.join(cache_path, "config.json")
    if not os.path.exists(config_path):
        os.makedirs(cache_path, exist_ok=True)
        default_config = {
            "machineID": str(uuid4())
        }
        with open(config_path, "w+") as f:
            f.write(json.dumps(default_config))
        return default_config
    else:
        with open(config_path, "r") as f:
            return json.loads(f.read())

if __name__ == "__main__":
    print(load_config())