from pathlib import Path
from typing import List
from pydantic.v1 import BaseModel, BaseSettings


class ExportMotionsRequest(BaseModel):
    scene_path: Path
    input_node_path: str
    input_exec_parm_name: str
    output_node_path: str
    output_exec_parm_name: str
    job_id: str
    motions: List
    output_path: Path
    avatar: str | None
    avatar_node_path: str
    avatar_parm_name: str
    geo_node_path: str


class CairosHoudiniConfig(BaseSettings):
    input_node_path: str = "/obj/geo_sequence_clips/input_json_to_pts"
    input_exec_parm_name: str = "cookbutton"
    output_node_path: str = "/obj/ropnet/char-gltf"
    output_exec_parm_name: str = "execute"
    avatar_node_path: str = "/obj/geo_avatar_rest/file2"
    avatar_parm_name: str = "file"
    geo_node_path: str = "/obj/geo_sequence_clips"
    server_port: int = 18861
    server_host: str = "cairos-houdini-server"


class CairosHoudiniSuccess(BaseModel):
    job_id: str
    gltf_path: Path


class CairosHoudiniError(BaseModel):
    error_message: str
