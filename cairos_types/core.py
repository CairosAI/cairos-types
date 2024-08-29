from pydantic.v1 import BaseModel, root_validator


class Motion(BaseModel):
    action: str
    filepath: str
    tags: str | list[str]

    @root_validator
    def check_motion(cls, values):
        import os

        action = values.get("action")
        filepath = values.get("filepath")
        tags = values.get("tags")
        if not os.path.isfile(filepath):
            raise ValueError(f"Motion {action} cannot be found at path {filepath}")
        return values


class Motions(BaseModel):
    key: str
    # tool_call_id: str
    entries: list[Motion]


class Animation(BaseModel):
    sequence: list[Motion]
    description: str


class MockMotion(BaseModel):
    action: str
    description: str


class MockMotions(BaseModel):
    motions: list[MockMotion]
