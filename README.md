# Banana Python SDK

Please see our usage docs in the official [Banana Documentation](https://docs.banana.dev/banana-docs/core-concepts/sdks/python)

## Developing on the SDK

Set up the environment and install the package in editable mode
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./
```

Set up a test directory to play around with the changes
```bash
mkdir tests
cd tests
touch test.py
```

Create some script
```python
from banana_dev import API

api = API("11111111-1111-1111-1111-111111111111")
projects, status = api.listProjects()
print('list',projects,status)

project, status = api.getProject(projects["results"][0]["id"])
print('get',project,status)

updatedProject, status = api.updateProject(projects["results"][0]["id"], {"maxReplicas": 2})
print('update',updatedProject,status)
```

Run it
```bash
python test.py
```
