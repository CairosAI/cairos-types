from pathlib import Path
from typing import List
from pydantic.v1 import BaseModel, BaseSettings


class ExportMotionsRequest(BaseModel):
    exposed_scene_path: Path
    exposed_input_node_path: str
    exposed_input_exec_parm_name: str
    exposed_output_node_path: str
    exposed_output_exec_parm_name: str
    exposed_job_id: str
    exposed_motions: List
    exposed_output_path: Path
    exposed_avatar: str | None
    exposed_avatar_node_path: str
    exposed_avatar_parm_name: str
    exposed_geo_node_path: str


class CairosHoudiniConfig(BaseSettings):
    input_node_path: str = "/obj/geo_sequence_clips/input_json_to_pts"
    input_exec_parm_name: str = "cookbutton"
    output_node_path: str = "/obj/ropnet/char-gltf"
    output_exec_parm_name: str = "execute"
    avatar_node_path: str = "/obj/geo_avatar_rest/file2"
    avatar_parm_name: str = "file"
    geo_node_path: str = "/obj/geo_sequence_clips"
    server_port: int = 18861


class CairosHoudiniSuccess(BaseModel):
    exposed_job_id: str
    exposed_gltf_path: Path

    def exposed_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)

    def exposed_dict(self, *args, **kwargs):
        return self.dict(*args, **kwargs)


class CairosHoudiniError(BaseModel):
    exposed_error_message: str

    def exposed_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)

    def exposed_dict(self, *args, **kwargs):
        return self.dict(*args, **kwargs)
