# Banana Python SDK

### Getting Started

Install via pip
`pip3 install banana-dev`

Get your API Key
- [Sign in / log in here](https://app.banana.dev)

Run:
```python
import os
import asyncio

# Set API Key Implicitly

os.environ['BANANA_APIKEY'] = '...'
models = {
    'model1': 'modelkey',
    'model2': 'modelkey',
}

from banana_dev import BananaClient

# Configure client implicitly
client = BananaClient(
    models = models
)

# Configure client explicitly
client = BananaClient(
    apikey = ...,
    models = models,
    model_name = 'model2', # use model2 as the default model
    model_key = 'modelkey', # use modelkey if models isn't configured
    json_results = True, # return results in json format, otherwise will return in pydantic model format
)

# Will save your configuration to ~/.banana/config.json
# future calls you can implicitly initiate the client without configuring it again

client = BananaClient()

model_inputs = {
    # a json specific to your model. For example:
    "imageURL":  "https://demo-images-banana.s3.us-west-1.amazonaws.com/image2.jpg"
}

# Optionally specify the model
# out = client.run(model_inputs, model_name = 'model1')
# can also call the client directly:
# out = client(model_inputs)

out = client.run(model_inputs)
print(out)

# Supports Asyncronous Calls

out = asyncio.run(client.async_run(model_inputs))
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
    ],
    "duration": 11.535236
}
```


Parse the server output:
```python
# if json_results is True, the output will be in json format
model_out = out["modelOutputs"][0]

# otherwise can access the output as a pydantic model
model_out = out.modelOutputs[0]
```
