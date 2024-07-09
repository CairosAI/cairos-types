from pydantic.v1 import BaseModel, root_validator


class Motion(BaseModel):
    action: str
    filepath: str
    tags: str | list[str]
    cause: str
    duration: float

    @root_validator
    def check_motion(cls, values):
        import os

        filepath = values.get("filepath")
        tags = values.get("tags")
        if not os.path.isfile(filepath):
            raise ValueError(f"Motion {tags} cannot be found at path {filepath}")
        duration = values.get("duration")
        if duration is None or duration <= 0:
            raise ValueError("Duration is None or nonpositive value.")
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
