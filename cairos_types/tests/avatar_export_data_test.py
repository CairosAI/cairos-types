import pytest
import tempfile
from typing import Generator, Any
from pathlib import Path

from cairos_types.houdini import AvatarExportData, AvatarExportDataWrapper

@pytest.fixture(scope='module')
def temp_paths() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".bgeo") as avatar, tempfile.NamedTemporaryFile(suffix=".bgeo.sc") as bgeo, tempfile.NamedTemporaryFile(suffix=".glb") as glb:
        yield [Path(avatar.name), Path(bgeo.name), Path(glb.name)]

@pytest.fixture(scope='module')
def avatar_export_data(temp_paths: list[Path]) -> AvatarExportData:
    return AvatarExportData(
        avatar_path=temp_paths[0],
        output_path=temp_paths[1],
        output_zip=temp_paths[2])

def test_avatar_export_data(avatar_export_data: AvatarExportData):
    data = AvatarExportDataWrapper(
        input_data=avatar_export_data,
        components=["bgeo", "fbx"]).convert_to_hou_format()

    print(data)
    assert isinstance(data["input_data"], dict)
    assert isinstance(data["components"], list)
    assert data["components"] == ["bgeo", "fbx"]
