from pydantic.v1 import BaseModel, root_validator
from datetime import datetime
import os

class Motion(BaseModel):
    sg_id: int
    description: str
    input: str # filepath of the motion
    created_at: datetime
    shot_description: str

    @root_validator(pre=True)
    def check_motion(cls, values):
        sg_id = values.get('sg_id')
        description = values.get('description')
        inputfile = values.get('input')
        shot_description = values.get('shot_description')
        # since a ShotGrid version always has an ID this is the least probable
        # case. Therefore we can use the sg_id to identify the motion in the
        # error messages
        if sg_id is None:
            raise ValueError('Motion missing id.')
        elif not isinstance(sg_id, int):
            raise ValueError(f'Motion with id {sg_id} should have an integer id.')

        if description is None or len(description) == 0:
            raise ValueError(f'Motion with id {sg_id} has missing or empty name.')
        if not os.path.isfile(inputfile):
            raise ValueError(f'Motion with id {sg_id} cannot be found at path {inputfile}')

        return values

class Motions(BaseModel):
    key: str
    # tool_call_id: str
    entries: list[Motion]

class Animation(BaseModel):
    sequence: list[Motion]
    description: str

class MockMotion(BaseModel):
    description: str
    input: str

class MockMotions(BaseModel):
    motions: list[MockMotion]
