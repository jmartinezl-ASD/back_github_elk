from pydantic import BaseModel
from typing import List

class userSchema(BaseModel):
    id: int
    login: str
    type: str
    html_url: str

class MembersResponse(BaseModel):
    members: List[userSchema]