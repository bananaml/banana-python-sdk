# Banana Python SDK

### Getting Started

Install via pip
```bash
pip3 install banana-dev
```

If integration testing against a local Potassium server:
```bash
export BANANA_SERVER=local
```
to call `http://localhost:8000/` directly. Be sure to unset in prod!


If deploying to prod:
[Sign in / log in here](https://app.banana.dev) to get your API and Model Keys

### Run:

```python
from banana_dev import Client

# Create a reference to your model on Banana
my_model = Client(
    api_key="YOUR_API_KEY", # Found in dashboard
    model_key="YOUR_MODEL_KEY", # Found in model view in dashboard
    url="https://YOUR_URL.run.banana.dev", # Found in model view in dashboard
)

# Specify the model's input JSON
inputs = {
    "prompt": "In the summer I like [MASK].",
}

# Call your model's inference endpoint on Banana
result, meta = my_model.call("/", inputs)
print(result)
```

