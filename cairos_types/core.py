from pydantic.v1 import BaseModel, root_validator, Field, validator
import os

class Motion(BaseModel):
    sg_id: int
    description: str
    input: str
    tags: list

    @root_validator
    def check_motion(cls, values):
        sg_id = values.get('sg_id')
        description = values.get('description')
        inputfile = values.get('input')
        tags = values.get('tags')

        # since a ShotGrid version always has an ID this is probably the least
        # probable case. Therefore we can use the sg_id to identify the motion
        # in the error messages
        if sg_id is None:
            raise ValueError(f'Motion missing id.')
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
