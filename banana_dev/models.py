from pydantic import BaseModel
from typing import Any, Optional


class BananaModel(BaseModel):
    """
    Base model for all Banana models
    """
    name: str
    key: str

class ModelResults(BaseModel):
    id: str
    message: str
    created: str
    apiVersion: str
    modelOutputs: Any
    duration: Optional[float] = None