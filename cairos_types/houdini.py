from pathlib import Path
from typing import List
from pydantic.v1 import BaseModel, BaseSettings
from uuid import UUID

class BaseHoudiniConfig(BaseSettings):
    server_port: int = 18861
    server_host: str = "cairos-houdini-server"

class SequencerConfig(BaseHoudiniConfig):
    input_top_node_path: str = "/obj/sequencer/output"
    data_input_node: str = "/obj/sequencer/sequencer/input_data"
    user_def_data_key: str = "motions"

    # Needed for setting the output file
    output_node_path: str = "/obj/sequencer/ropnet/char-gltf"
    output_exec_parm_name: str = "execute"

    # For loading the user's avatar
    avatar_node_path: str = "/obj/geo_avatar_rest/file2"
    avatar_parm_name: str = "file"

    scene_path: Path

class HoudiniError(BaseModel):
    error_message: str

class SequencerRequest(BaseModel):
    job_id: tuple[str, UUID]
    motions: List
    output_path: Path
    avatar: str | None
    config: SequencerConfig

class SequencerSuccess(BaseModel):
    job_id: tuple[str, UUID]
    gltf_path: Path

class AvatarIngestConfig(BaseHoudiniConfig):
    data_input_node: str = "/obj/ingest/character/RPC_DATA_COMES_HERE"
    user_def_data_key: str = "io_paths"
    render_top_node: str = "/obj/ingest/output"

    scene_path: Path

class AvatarIngestRequest(BaseModel):
    config: AvatarIngestConfig
    input_avatar_path: Path
    output_avatar_path: Path

class AvatarIngestSuccess(BaseModel):
    path: Path
