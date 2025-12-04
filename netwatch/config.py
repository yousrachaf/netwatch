from pydantic import BaseModel
from typing import List, Literal

CheckType=Literal["ping","http","tcp"]
class target(BaseModel):
    name:str
    host:str
    type: CheckType
    port: int | None=None
    path: str | None = None

def default_targets() -> List[Target]:
     return [
        Target(name="Google DNS", host="8.8.8.8", type="ping"),
        Target(name="GitHub API", host="api.github.com", type="http", path="/"),
        Target(name="SSH Prod", host="example.com", type="tcp", port=22),
    ]