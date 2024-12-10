from pathlib import Path
from typing import Literal, TypeAlias, get_args
from pydantic.v1 import BaseModel, BaseSettings, root_validator, validator, Field
from uuid import UUID
from cairos_types.core import Motion

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
    data_input_node: str = f"{prefix}/sequencer/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/output"

class SequencerAvatarData(BaseModel):
    input: Path
    output_bgeo: Path
    output_gltf: Path

    @validator('input')
    def check_avatar_filepath_exists(cls, v):
        if not v.is_file():
            raise ValueError(f'Avatar for sequencing job does not exist at {v}')
        # TODO check suffix here as well
        return v

    @validator('output_bgeo')
    def check_bgeo_suffix(cls, v):
        if not v.suffix == '.bgeo':
            raise ValueError(f'output_bgeo field should be a path to a file with `.bgeo` extension.')
    @validator('output_gltf')
    def check_gltf_suffix(cls, v):
        if not v.suffix == '.gltf':
            raise ValueError(f'output_gltf field should be a path to a file with `.gltf` extension.')


class SequencerDataWrapper(BaseHoudiniData):
    avatar: SequencerAvatarData
    animations: dict[str, list[str | int | float]]

    @root_validator(pre=True)
    def convert_animations_to_hou_format(cls, values):
        # Houdini does not support list[dict] currently (even though the
        # documentation states otherwise). Since we usually contain motions in a
        # list[Motion] here we will reshape it to a dict of lists. The dict
        # follows the shape of a Motion, but each key has a list of values (for
        # each motion respectively).

        reshaped = {}
        motions: list[Motion] = values['animations']
        for m in motions:
            as_dict = m.dict()
            for key, value in as_dict.items():
                if isinstance(value, list):
                    if isinstance(value[0], str):
                        value = ';'.join(value)
                    else:
                        raise ValueError('Motion attributes of type list can only have string elements.')
                if key in reshaped:
                    reshaped[key].append(value)
                else:
                    reshaped[key] = [value]

        values['animations'] = reshaped
        return values

    def __init__(self,
                 avatar: SequencerAvatarData,
                 animations: list[Motion]):
        d = locals()
        d.pop('self')
        super().__init__(**d)


class SequencerRequest(BaseModel):
    job_id: tuple[str, UUID]
    config: SequencerConfig
    data: SequencerDataWrapper

class SequencerSuccess(BaseModel):
    request: SequencerRequest

    bgeo: Path
    gltf: Path


    # @root_validator(pre=True)
    # def interp_paths(cls, values):
    #     try:
    #         values.update({'fbx': Path(values['request'].data.avatar.output, 'output.fbx'),
    #                        'gltf': Path(values['request'].data.avatar.output,
    #                                     'output-gltf-char.glb')
    #                        })
    #     except Exception as e:
    #         raise e
    #     return values

    # Finally we check if they are existing files on mothership3. The type
    # annotations have `| None` so that LSP does not require passing them when
    # instantiating the object.
    @root_validator
    def check_paths_exist(cls, values):
        if not values['bgeo'].is_file():
            raise ValueError(f'Path to BGEO file does not exist at {values["bgeo"]}')

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
    input_avatar: Path
    input_mapping: Path
    output_bgeo: Path
    output_gltf: Path
    output_thumbnail: Path
    output_skelref: Path

    @root_validator(pre=True)
    def generate_mapping_path(cls, values):
        try:
            m = values['input_mapping']
            # `get_args` is a hack to get generic parameters of type, types with
            # generic parameters cannot be used in `isinstance()` and `issubclass()`
            if m in get_args(AvatarMapping):
                values['input_mapping'] = Path(
                    '/mothership3/projects/crs/global/mapping',
                    m + '.csv')
            elif not isinstance(m, Path):
                values['input_mapping'] = Path(m)
        except KeyError:
            raise ValueError('A name for joint mapping table must be provided.')
        return values

    @root_validator
    def check_files_exist(cls, values):
        if not values['input_avatar'].is_file():
            raise ValueError(f'Input file does not exist at {values["input_avatar"]}')

        if not values['input_mapping'].is_file(): # TODO add check if the prefix of
                                            # the path is indeed
                                            # '/mothership3/projects/crs/global/mapping'
            raise ValueError(f'Joint mapping table file does not exist at {values["input_mapping"]}')
        if not values['output_bgeo'].suffix == '.bgeo':
            raise ValueError(f'output_bgeo field should be a path to a file with `.bgeo` extension.')
        if not values['output_gltf'].suffix == '.gltf':
            raise ValueError(f'output_gltf field should be a path to a file with `.gltf` extension.')
        if not values['output_thumbnail'].suffix == '.png':
            raise ValueError(f'output_thumbnail field should be a path to a file with `.png` extension.')
        if not values['output_skelref'].suffix == '.png':
            raise ValueError(f'output_skelref field should be a path to a file with `.png` extension.')
        return values

    # overriding init to correctly hint acceptable types for mapping and play
    # nice with the LSP
    def __init__(self,
                 input_avatar: Path,
                 input_mapping: AvatarMapping | Path,
                 output_bgeo: Path,
                 output_gltf: Path,
                 output_thumbnail: Path,
                 output_skelref: Path):
        d = locals()
        d.pop('self')
        super().__init__(**d)

class AvatarIngestDataWrapper(BaseHoudiniData):
    ingest: AvatarIngestData

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
