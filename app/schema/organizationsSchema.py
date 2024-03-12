from pydantic import BaseModel
from typing import List
# Submodelos
class owner_details():
    id: int
    login: str
    type: str

# Modelos
class repositorySchema(BaseModel):
    id: int
    name: str
    html_url: str
    owner: List[owner_details]
    issues_url: str
    pull_url: str
    has_issues: bool
    open_issues_count: int
    open_issues: int
    
    
class MembersResponse(BaseModel):
    repositorys: List[repositorySchema]