from pathlib import Path
from typing import List
from pydantic.v1 import BaseModel, BaseSettings
from uuid import UUID

class ExportMotionsRequest(BaseModel):
    scene_path: Path
    input_top_node_path: str
    output_node_path: str
    output_exec_parm_name: str
    job_id: tuple[str, UUID]
    motions: List
    output_path: Path
    avatar: str | None
    avatar_node_path: str
    avatar_parm_name: str


class CairosHoudiniConfig(BaseSettings):
    input_top_node_path: str = "/obj/geo_sequence_clips/topnet1"
    data_input_node: str = "/obj/geo_sequence_clips/input_data"
    user_def_data_key: str = "motions"

    output_node_path: str = "/obj/ropnet/char-gltf"
    output_exec_parm_name: str = "execute"
    avatar_node_path: str = "/obj/geo_avatar_rest/file2"
    avatar_parm_name: str = "file"
    server_port: int = 18861
    server_host: str = "cairos-houdini-server"


class CairosHoudiniSuccess(BaseModel):
    job_id: str
    gltf_path: Path


class CairosHoudiniError(BaseModel):
    error_message: str
