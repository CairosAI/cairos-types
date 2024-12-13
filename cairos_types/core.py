from pydantic.v1 import BaseModel, root_validator, Field, validator
import os

class Motion(BaseModel):
    class Config:
        allow_population_by_field_name = True

    sg_id: int = Field(..., alias='id')
    # TODO remove later. This alias is temporary, while we still have no descriptions
    description: str = Field(..., alias='sg_mocap_desc_emotion')
    input: str = Field(..., alias='sg_file_animation')
    tags: list

    @root_validator(pre=True)
    def map_from_sg(cls, values):
        try:
            if not 'sg_id' in values:
                values.update({'sg_id': values.pop('id')})
            if not 'description' in values:
                values.update({'description': values.pop('sg_mocap_desc_emotion')})
            if not 'input' in values:
                values.update({'input': values.pop('sg_file_animation')})

        except Exception as e:
            raise e

        return values

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
