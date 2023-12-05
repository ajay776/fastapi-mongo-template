from pydantic import BaseModel
from typing import Optional, Any


class CommonResponseSchema(BaseModel):
    type: str
    status_code: int
    message: str
    data: Optional[Any]
