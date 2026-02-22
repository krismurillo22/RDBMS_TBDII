from dataclasses import dataclass

@dataclass(frozen=True)
class DbObject:
    obj_type: str 
    schema: str
    name: str
