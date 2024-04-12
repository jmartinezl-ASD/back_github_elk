from pydantic import BaseModel


class userSchema(BaseModel):
    id: int
    login: str
    type: str
    html_url: str
