import pytest
import tempfile
from typing import Generator, Any
from cairos_types.core import Motion, Motions
from pathlib import Path

from cairos_types.houdini import ExportDataWrapper, ExportData

@pytest.fixture(scope='module')
def temp_paths() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".bgeo") as avatar, tempfile.NamedTemporaryFile(suffix=".bgeo.sc") as bgeo, tempfile.NamedTemporaryFile(suffix=".glb") as glb:
        yield [Path(avatar.name), Path(bgeo.name), Path(glb.name)]

@pytest.fixture(scope='module')
def export_data(temp_paths: list[Path]) -> ExportData:
    return ExportData(
        sequencer_product=temp_paths[0],
        output_path=temp_paths[1],
        output_zip=temp_paths[2])

def test_export_data(export_data: ExportData):
    data = ExportDataWrapper(
        input_data=export_data,
        components=["bgeo", "fbx"]).convert_to_hou_format()

    assert isinstance(data["input_data"], dict)
    assert isinstance(data["components"], list)
