from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class BananaModel:
    """
    Base model for all Banana models
    """
    name: str
    key: str

# @dataclass
# class ModelResults:
#     id: str
#     message: str
#     created: str
#     apiVersion: str
#     modelOutputs: Any
#     duration: Optional[float] = None