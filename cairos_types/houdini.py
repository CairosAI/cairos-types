from pathlib import Path
from typing import Literal, TypeAlias, get_args
from pydantic.v1 import BaseModel, BaseSettings, root_validator, validator, Field
from uuid import UUID

class BaseHoudiniConfig(BaseSettings):
    server_port: int = 18861
    server_host: str = "cairos-houdini-server"

class BaseHoudiniData(BaseModel):
    def btl_list_fields(self):
        return list(self.schema().get('properties').keys())

class SequencerConfig(BaseHoudiniConfig):
    scene_path: Path
    # since we have a single hip file, that will be used for several operations
    # a node graph prefix is handy
    prefix: str = "/obj/sequencer"
    data_input_node: str = f"{prefix}/sequencer/input_data"
    render_top_node: str = f"{prefix}/output"

class SequencerAvatarData(BaseModel):
    filepath: Path
    output_bgeo: Path
    output_gltf: Path

    @validator('filepath')
    def check_avatar_filepath_exists(cls, v):
        if not v.is_file():
            raise ValueError(f'Avatar for sequencing job does not exist at {v}')

class SequencerDataWrapper(BaseHoudiniData):
    avatar: SequencerAvatarData
    animations: list

class SequencerRequest(BaseModel):
    job_id: tuple[str, UUID]
    config: SequencerConfig
    data: SequencerDataWrapper

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
    render_top_node: str = f"{prefix}/output"

AvatarMapping: TypeAlias = Literal['mixamo'] # more to come in the near future

class AvatarIngestData(BaseModel):
    input_path: Path
    output_path: Path # directory, ensured in validator
    mapping: Path

    @root_validator(pre=True)
    def generate_mapping_path(cls, values):
        try:
            m = values['mapping']
            # `get_args` is a hack to get generic parameters of type, types with
            # generic parameters cannot be used in `isinstance()` and `issubclass()`
            if m in get_args(AvatarMapping):
                values['mapping'] = Path(
                    '/mothership3/projects/crs/global/mapping',
                    m + '.csv')
            elif not isinstance(m, Path):
                values['mapping'] = Path(m)
        except KeyError:
            raise ValueError('A name for joint mapping table must be provided.')
        return values

    @root_validator
    def check_files_exist(cls, values):
        if not values['input_path'].is_file():
            raise ValueError(f'Input file does not exist at {values["input_path"]}')
        if not values['output_path'].is_dir():
            raise ValueError(f'Output path should be a directory, received {values["output_path"]}')
        if not values['mapping'].is_file(): # TODO add check if the prefix of
                                            # the path is indeed
                                            # '/mothership3/projects/crs/global/mapping'
            raise ValueError(f'Joint mapping table file does not exist at {values["mapping"]}')
        return values

    # overriding init to correctly hint acceptable types for mapping and play
    # nice with the LSP
    def __init__(self, input_path: Path, output_path: Path, mapping: AvatarMapping | Path):
        d = locals()
        d.pop('self')
        super().__init__(**d)

class AvatarIngestDataWrapper(BaseHoudiniData):
    avatar: AvatarIngestData # TODO THIS IS NOT THE CORRECT ATTRIBUTE NAME, AS

class AvatarIngestRequest(BaseModel):
    config: AvatarIngestConfig
    data: AvatarIngestDataWrapper

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
