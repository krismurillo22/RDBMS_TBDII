from dataclasses import dataclass

@dataclass(frozen=True)
class DbObject:
    obj_type: str   # "table", "view"
    schema: str
    name: str
