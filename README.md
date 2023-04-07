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
import banana_dev as banana

# Your credentials. Can be empty strings if testing against a local server.
api_key = "demo" # YOUR_API_KEY
model_key = "carrot" # YOUR_MODEL_KEY

model_inputs = {
    # a json specific to your model. For example:
    "imageURL":  "https://demo-images-banana.s3.us-west-1.amazonaws.com/image2.jpg"
}

out = banana.run(api_key, model_key, model_inputs)
print(out)
```

Return type:
```python
{
    "id": "12345678-1234-1234-1234-123456789012", 
    "message": "success", 
    "created": 1649712752, 
    "apiVersion": "26 Nov 2021", 
    "modelOutputs": [
        {
            # a json specific to your model. In this example, the caption of the image
            "caption": "a baseball player throwing a ball"
        }
    ]
}
```

Parse the server output:
```python
model_out = out["modelOutputs"][0]
```