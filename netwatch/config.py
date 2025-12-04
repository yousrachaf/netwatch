from pydantic import BaseModel
from typing import List, Literal


# Types de checks supportés
CheckType = Literal["ping", "http", "tcp"]


class Target(BaseModel):
    """Définition d'une cible à surveiller."""
    name: str
    host: str
    type: CheckType
    port: int | None = None    # pour TCP
    path: str | None = None    # pour HTTP


def default_targets() -> List[Target]:
    """Liste des cibles surveillées par défaut."""
    return [
        Target(name="Google DNS", host="8.8.8.8", type="ping"),
        Target(name="GitHub API", host="api.github.com", type="http", path="/"),
        Target(name="SSH Prod", host="example.com", type="tcp", port=22),
    ]
