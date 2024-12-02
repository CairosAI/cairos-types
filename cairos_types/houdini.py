from pathlib import Path
from typing import Literal, TypeAlias
from pydantic.v1 import BaseModel, BaseSettings, root_validator
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
    fbx: Path | None
    gltf: Path | None

    @root_validator(pre=True)
    def check_paths_exist(cls, values):
        if not values['fbx'].is_file():
            raise ValueError('Path to FBX file does not exist.')

        if not values['gltf'].is_file():
            raise ValueError('Path to glTF file does not exist.')

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

    @property
    def mapping_path(self) -> Path:
        return Path('/mothership3/projects/crs/global/mapping', self.mapping, '.csv')

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
    def check_paths_exist(cls, values):
        if not values['thumbnail'].is_file():
            raise ValueError('Path to avatar thumbnail does not exist.')

        if not values['gltf'].is_file():
            raise ValueError('Path to glTF file does not exist.')

        return values

class HoudiniError(BaseModel):
    error_message: str

