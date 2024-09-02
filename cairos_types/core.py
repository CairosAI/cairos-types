from pydantic.v1 import BaseModel, root_validator
import os

class Motion(BaseModel):
    sg_id: int
    action: str
    filepath: str
    tags: str

    @root_validator
    def check_motion(cls, values):
        sg_id = values.get('sg_id')
        action = values.get('action')
        filepath = values.get('filepath')
        tags = values.get('tags')

        # since a ShotGrid version always has an ID this is probably the least
        # probable case. Therefore we can use the sg_id to identify the motion
        # in the error messages
        if sg_id is None:
            if not isinstance(sg_id, int):
                raise ValueError(f'Motion with id {sg_id} should have an integer id.')
        else:
            raise ValueError(f'Motion missing id.')

        if action is None or len(action) == 0:
            raise ValueError(f'Motion with id {sg_id} has missing or empty name.')

        if not os.path.isfile(filepath):
            raise ValueError(f'Motion with id {sg_id} cannot be found at path {filepath}')

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
