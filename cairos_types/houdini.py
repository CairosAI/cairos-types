from pathlib import Path
from typing import Literal, TypeAlias
from pydantic.v1 import BaseModel, BaseSettings, root_validator, validator, Field
from uuid import UUID

class BaseHoudiniConfig(BaseSettings):
    server_port: int = 18861
    server_host: str = "cairos-houdini-server"

class SequencerConfig(BaseHoudiniConfig):
    scene_path: Path
    # since we have a single hip file, that will be used for several operations
    # a node graph prefix is handy
    prefix: str = "/obj/sequencer"
    data_input_node: str = f"{prefix}/sequencer/RPC_DATA_COMES_HERE"
    user_def_data_key: str = "cairos_data"
    render_top_node: str = f"{prefix}/output"

class SequencerAvatarData(BaseModel):
    filepath: str
    output: str

class SequencerData(BaseModel):
    avatar: SequencerAvatarData
    motions: list

class SequencerRequest(BaseModel):
    job_id: tuple[str, UUID]
    config: SequencerConfig
    data: SequencerData

class SequencerSuccess(BaseModel):
    request: SequencerRequest
    # these fields will be computed from the info in request...
    fbx: Path | None = Field(...)
    gltf: Path | None = Field(...)

    # ...using a `pre=True` root_validator
    @root_validator(pre=True)
    def interp_paths(cls, values):
        try:
            values.update({'fbx': Path(values['request'].data.avatar.output, 'output.fbx'),
                           'gltf': Path(values['request'].data.avatar.output,
                                        'output-gltf-char.glb')
                           })
        except Exception as e:
            raise e
        return values

    # Finally we check if they are existing files on mothership3. The type
    # annotations have `| None` so that LSP does not require passing them when
    # instantiating the object.
    @root_validator
    def check_paths_exist(cls, values):
        if not values['fbx'].is_file():
            raise ValueError(f'Path to FBX file does not exist at {values["fbx"]}')

        if not values['gltf'].is_file():
            raise ValueError(f'Path to glTF file does not exist at {values["gltf"]}')

        return values

class AvatarIngestConfig(BaseHoudiniConfig):
    scene_path: Path
    prefix: str = "/obj/ingest"
    data_input_node: str = f"{prefix}/character/RPC_DATA_COMES_HERE"
    user_def_data_key: str = "cairos_data"
    render_top_node: str = f"{prefix}/output"

AvatarMapping: TypeAlias = Literal['mixamo'] # more to come in the near future

class AvatarIngestData(BaseModel):
    input_path: str
    output_path: str # directory
    mapping: AvatarMapping
    mapping_path: Path

    # @validator('mapping_path', pre=True)
    # def generate_mapping_path(cls, v)
    @root_validator(pre=True)
    def generate_mapping_path(cls, values):
        try:
            values.update(
                {'mapping_path': Path(
                    '/mothership3/projects/crs/global/mapping',
                    values['mapping'] + '.csv')
                })
        except KeyError:
            raise ValueError('A name for joint mapping table must be provided.')
        return values

    @validator('mapping_path')
    def check_mapping_file_exists(cls, v):
        if not v.is_file():
            raise ValueError(f'Joint mapping table file does not exist at {v}')
        return v

class AvatarIngestRequest(BaseModel):
    config: AvatarIngestConfig
    data: AvatarIngestData
    # input_avatar_path: Path
    # output_avatar_path: Path

class AvatarIngestSuccess(BaseModel):
    request: AvatarIngestRequest
    gltf: Path | None
    thumbnail: Path | None

    @root_validator(pre=True)
    def interp_paths(cls, values):
        try:
            values.update({'gltf': Path(values['request'].data.output_path,
                                        'ingest.glb'),
                           'thumbnail': Path(values['request'].data.output_path, 'thumbnail.png')
                           })
        except Exception as e:
            raise e
        return values

    @root_validator
    def check_paths_exist(cls, values):
        if not values['thumbnail'].is_file():
            raise ValueError(f'Path to avatar thumbnail does not exist at {values["thumbnail"]}')

        if not values['gltf'].is_file():
            raise ValueError(f'Path to glTF file does not exist at {values["gltf"]}')

        return values

class HoudiniError(BaseModel):
    error_message: str

