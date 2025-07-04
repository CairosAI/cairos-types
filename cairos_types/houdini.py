from pathlib import Path
from typing import Literal, TypeAlias, get_args
from pydantic.v1 import BaseModel, BaseSettings, root_validator, validator, ConfigDict, Extra
from uuid import UUID
from cairos_types.core import Motion
import json

class BaseHoudiniConfig(BaseSettings):
    server_port: int = 18861
    server_host: str = "cairos-houdini-server"
    debug_scene_directory: Path | None = None
    logs_host: str = "loki"
    logs_port: int = 3100

    @property
    def logs_address(self) -> str:
        return f'http://{self.logs_host}:{self.logs_port}/loki/api/v1/push'

class BaseHoudiniData(BaseModel):
    def btl_list_fields(self):
        return list(self.schema().get('properties').keys())

class MsgQueueConfig(BaseSettings, extra=Extra.ignore):
    model_config = ConfigDict(extra=Extra.ignore)

    broker_name: str = "cairos"
    msg_queue_name_to: str = "cairos.houdini_request"
    msg_queue_name_from: str = "cairos.houdini_response"
    msg_queue_username: str
    msg_queue_password: str
    msg_queue_host: str = "rabbitmq"
    request_timeout: int = 240
    request_retry_interval: int = 2
    backend: str = "rpc://"
    @property
    def broker_url(self) -> str:
        return f"amqp://{self.msg_queue_username}:{self.msg_queue_password}@{self.msg_queue_host}:5672//"

class Context(BaseSettings):
    username: str
    action: str | None = None
    thread: str | None = None
    message: str | None = None
    scene: str | None = None
    animation: str | None = None
    avatar: str | None = None

class SequencerConfig(BaseHoudiniConfig):
    scene_path: Path
    # since we have a single hip file, that will be used for several operations
    # a node graph prefix is handy
    prefix: str = "/obj/sequencer"
    data_input_node: str = f"{prefix}/sequencer/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/output"

class SequencerOutput(BaseHoudiniData):
    output_bgeo: Path
    output_gltf: Path


class SequencerDataWrapper(BaseHoudiniData):
    animations: list[Motion]
    output: SequencerOutput

    def convert_animations_to_hou_format(self) -> dict[str, dict[str, str | list[str | int | float]]]:
        self_as_dict = json.loads(self.json())

        # we can assume that motions is list, since pydantic has validated it at
        # this point
        motions: list[dict[str, str | int]] = self_as_dict['animations']

        # Houdini does not support list[dict] currently (even though the
        # documentation states otherwise). Since we usually contain motions in a
        # list[Motion] here we will reshape it to a dict of lists. The dict
        # follows the shape of a Motion, but each key has a list of values (for
        # each motion respectively).
        reshaped = {}

        for m in motions:
            for key, value in m.items():
                if isinstance(value, list):
                    if len(value) > 0:
                        if isinstance(value[0], str):
                            value = ';'.join(value)
                        else:
                            raise ValueError('Motion attributes of type list can only have string elements.')
                    else:
                        value = ''

                if key in reshaped:
                    reshaped[key].append(value)
                else:
                    reshaped[key] = [value]

        self_as_dict.update({'animations': reshaped})

        return self_as_dict

class SequencerRequest(BaseModel):
    job_id: tuple[str, UUID]
    config: SequencerConfig
    context: Context
    data: SequencerDataWrapper

class SequencerSuccess(BaseModel):
    job_id: tuple[str, UUID]
    output_bgeo: Path
    output_gltf: Path

    @root_validator
    def check_paths_exist(cls, values):
        if not values['output_bgeo'].is_file():
            raise ValueError(f'Path to BGEO file does not exist at {values["output_bgeo"]}')

        if not values['output_gltf'].is_file():
            raise ValueError(f'Path to glTF file does not exist at {values["output_gltf"]}')

        return values

class RetargetConfig(BaseHoudiniConfig):
    scene_path: Path
    prefix: str = "/obj/retarget"
    data_input_node: str = f"{prefix}/retarget/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/output"

class RetargetSuccess(BaseModel):
    job_id: tuple[str, UUID]
    output_bgeo: Path
    output_gltf: Path

    @root_validator
    def check_paths_exist(cls, values):
        if not values["output_bgeo"].is_file():
            raise ValueError(f'Path to BGEO file does not exist at {values["output_bgeo"]}')

        if not values['output_gltf'].is_file():
            raise ValueError(f'Path to glTF file does not exist at {values["output_gltf"]}')

        return values

class RetargetInput(BaseModel):
    sequencer_bgeo: Path
    avatar_bgeo: Path

    @validator('sequencer_bgeo')
    def check_sequencer_bgeo_exists(cls, v: Path):
        if not v.is_file():
            raise ValueError(f"Sequencer bgeo does not exist {v}")

        return v

    @validator('avatar_bgeo')
    def check_avatar_bgeo_exists(cls, v: Path):
        if not v.is_file():
            raise ValueError(f"Avatar bgeo does not exist {v}")

        return v

class RetargetOutput(BaseModel):
    output_bgeo: Path
    output_gltf: Path

    @validator('output_bgeo')
    def check_bgeo_suffix(cls, v: Path):
        suffixes = v.suffixes
        if len(suffixes) != 2 or suffixes[0] != '.bgeo' or suffixes[1] != '.sc':
            raise ValueError(f'output_bgeo field should be a path to a file with `.bgeo.sc` extension.')
        return v

    @validator('output_gltf')
    def check_gltf_suffix(cls, v):
        if not v.suffix == '.glb': # probably more suffixes will be possible
            raise ValueError(f'output_gltf field should be a path to a file with `.glb` extension.')
        return v


class RetargetDataWrapper(BaseModel):
    input: RetargetInput
    output: RetargetOutput

    def convert_to_hou_format(self) -> dict[str, dict[str, str | list[str | int | float]]]:
        self_as_dict = json.loads(self.json())

        return self_as_dict

class RetargetRequest(BaseModel):
    job_id: tuple[str, UUID]
    config: RetargetConfig
    context: Context
    data: RetargetDataWrapper

class ExportConfig(BaseHoudiniConfig):
    scene_path: Path
    # since we have a single hip file, that will be used for several operations
    # a node graph prefix is handy
    prefix: str = "/obj/export"
    data_input_node: str = f"{prefix}/export/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/topnet1"


class ExportData(BaseModel):
    sequencer_product: Path
    output_path: Path
    output_zip: Path

class ExportDataWrapper(BaseModel):
    input_data: ExportData

    def convert_to_hou_format(self) -> dict[str, dict[str, str | list[str | int | float]]]:
        # TODO
        self_as_dict = json.loads(self.json())
        return self_as_dict

class ExportSuccess(BaseModel):
    job_id: tuple[str, UUID]
    output_path: Path
    output_zip: Path

    @root_validator
    def check_paths_exist(cls, values):
        if not values['output_path'].is_dir():
            raise ValueError(f'Output path does not exist at {values["output_path"]}')
        if not values['output_zip'].is_file():
            raise ValueError(f'Output zip does not exist at {values["output_zip"]}')

        return values

class ExportRequest(BaseModel):
    job_id: tuple[str, UUID]
    config: ExportConfig
    context: Context
    data: ExportDataWrapper

ExportType: TypeAlias = Literal['.glb', '.fbx', '.zip']


class AvatarExportConfig(BaseHoudiniConfig):
    scene_path: Path
    # since we have a single hip file, that will be used for several operations
    # a node graph prefix is handy
    prefix: str = "/obj/export_avatar"
    data_input_node: str = f"{prefix}/export/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/topnet1"


class AvatarExportData(BaseModel):
    avatar_path: Path
    output_path: Path
    output_zip: Path

class AvatarExportDataWrapper(BaseModel):
    input_data: AvatarExportData

    def convert_to_hou_format(self) -> dict[str, dict[str, str | list[str | int | float]]]:
        # TODO
        self_as_dict = json.loads(self.json())
        return self_as_dict

class AvatarExportSuccess(BaseModel):
    avatar_id: UUID
    output_path: Path
    output_zip: Path

    @root_validator
    def check_paths_exist(cls, values):
        if not values['output_path'].is_dir():
            raise ValueError(f'Output path does not exist at {values["output_path"]}')
        if not values['output_zip'].is_file():
            raise ValueError(f'Output zip does not exist at {values["output_zip"]}')

        return values

class AvatarExportRequest(BaseModel):
    avatar_id: UUID
    config: AvatarExportConfig
    context: Context
    data: AvatarExportDataWrapper

class AvatarUploadConfig(BaseHoudiniConfig):
    scene_path: Path
    prefix: str = "/obj/upload"
    data_input_node: str = f"{prefix}/character/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/output"

AvatarPreset: TypeAlias = Literal['mixamo']
AvatarMapping: TypeAlias = AvatarPreset | Path | bytes # more to come in the near future


class AvatarUploadData(BaseModel):
    avatar_id: UUID
    input_avatar: Path
    output_bgeo: Path
    output_gltf: Path
    output_thumbnail: Path
    output_skelref: Path
    output_joint_paths: Path

    @root_validator
    def check_files_exist(cls, values):
        if not values['input_avatar'].is_file():
            raise ValueError(f'Input file does not exist at {values["input_avatar"]}')
        if not values['output_bgeo'].suffix == '.bgeo':
            raise ValueError(f'output_bgeo field should be a path to a file with `.bgeo` extension.')
        if not values['output_gltf'].suffix == '.glb':
            raise ValueError(f'output_gltf field should be a path to a file with `.glb` extension.')
        if not values['output_thumbnail'].suffix == '.png':
            raise ValueError(f'output_thumbnail field should be a path to a file with `.png` extension.')
        if not values['output_skelref'].suffix == '.png':
            raise ValueError(f'output_skelref field should be a path to a file with `.png` extension.')
        return values

    # overriding init to correctly hint acceptable types for mapping and play
    # nice with the LSP
    def __init__(self,
                 avatar_id: UUID,
                 input_avatar: Path,
                 output_bgeo: Path,
                 output_gltf: Path,
                 output_thumbnail: Path,
                 output_skelref: Path,
                 output_joint_paths: Path | None = None):
        d = locals()
        d.pop('self')
        super().__init__(**d)

class AvatarUploadDataWrapper(BaseHoudiniData):
    ingest: AvatarUploadData

class AvatarUploadRequest(BaseModel):
    config: AvatarUploadConfig
    context: Context
    data: AvatarUploadDataWrapper

class AvatarUploadSuccess(BaseModel):
    avatar_id: UUID
    output_bgeo: Path
    output_gltf: Path
    output_thumbnail: Path
    output_skelref: Path
    output_joint_paths: Path | None

    @root_validator
    def check_paths_exist(cls, values):
        if not values['output_bgeo'].is_file():
            raise ValueError(f'No bgeo file found at path {values["output_bgeo"]}')

        if not values['output_gltf'].is_file():
            raise ValueError(f'No glTF file found at path {values["output_gltf"]}')

        # These are commented out temporarily, while we figure out how to
        # prevent OpenGL ROP from crashing hython

        # if not values['output_thumbnail'].is_file():
        #     raise ValueError(f'Path to avatar thumbnail does not exist at {values["output_thumbnail"]}')
        # if not values['output_skelref'].is_file():
        #     raise ValueError(f'Path to avatar skelref does not exist at {values["output_skelref"]}')

        return values

class AvatarAutorigData(BaseModel):
    avatar_id: UUID
    input_avatar: Path
    output_bgeo: Path
    output_gltf: Path

    @root_validator
    def check_files_exist(cls, values):
        if not values['input_avatar'].is_file():
            raise ValueError(f'Input file does not exist at {values["input_avatar"]}')

        if not values['output_bgeo'].suffix == '.bgeo':
            raise ValueError(f'output_bgeo field should be a path to a file with `.bgeo` extension.')
        if not values['output_gltf'].suffix == '.glb':
            raise ValueError(f'output_gltf field should be a path to a file with `.glb` extension.')

        return values

class AvatarAutorigConfig(BaseHoudiniConfig):
    scene_path: Path
    prefix: str = "/obj/autorig"
    data_input_node: str = f"{prefix}/character/RPC_DATA_COMES_HERE"
    render_top_node: str = f"{prefix}/output"

class AvatarAutorigDataWrapper(BaseHoudiniData):
    ingest: AvatarAutorigData

    def convert_to_hou_format(self) -> dict[str, dict[str, str | list[str | int | float]]]:
        # TODO
        self_as_dict = json.loads(self.json())
        return self_as_dict

class AvatarAutorigRequest(BaseModel):
    avatar_id: UUID
    config: AvatarAutorigConfig
    context: Context
    data: AvatarAutorigDataWrapper

class AvatarAutorigSuccess(BaseModel):
    avatar_id: UUID
    output_bgeo: Path
    output_gltf: Path

    @root_validator
    def check_paths_exist(cls, values):
        if not values['output_bgeo'].is_file():
            raise ValueError(f'Path to bgeo file does not exist at {values["output_bgeo"]}')

        if not values['output_gltf'].is_file():
            raise ValueError(f'Path to glTF file does not exist at {values["output_gltf"]}')

        return values


class HoudiniError(BaseModel):
    error_message: str
