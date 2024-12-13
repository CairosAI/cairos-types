from cairos_types.houdini import AvatarIngestData, AvatarIngestDataWrapper
import tempfile
from typing import Generator, Any
import pytest
from pathlib import Path

@pytest.fixture(scope='module')
def existing_file() -> Path:
    return Path(Path(__file__).parent.parent.parent , 'pyproject.toml')

@pytest.fixture(scope='module')
def existing_dir(existing_file: Path) -> Path:
    return existing_file.parent

@pytest.fixture(scope='module')
def temp_paths() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".fbx") as avatar,\
         tempfile.NamedTemporaryFile(suffix=".bgeo") as bgeo,\
         tempfile.NamedTemporaryFile(suffix=".glb") as glb, \
         tempfile.NamedTemporaryFile(suffix=".png") as png, \
         tempfile.NamedTemporaryFile(suffix=".png") as skel, \
         tempfile.NamedTemporaryFile(suffix=".csv") as mapping:
        yield [Path(avatar.name),
               Path(bgeo.name),
               Path(glb.name),
               Path(png.name),
               Path(skel.name),
               Path(mapping.name)]

def test_avatar_ingest_data_creation(temp_paths: list[Path],
                                     existing_dir: Path):
    obj = AvatarIngestData(
        input_avatar=temp_paths[0],
        output_bgeo=temp_paths[1],
        output_gltf=temp_paths[2],
        output_thumbnail=temp_paths[3],
        output_skelref=temp_paths[4],
        input_mapping='mixamo') # LSP does not complain, even
                          # completion works

    assert isinstance(obj.input_mapping, Path)
    assert obj.input_avatar == temp_paths[0]
    assert obj.output_bgeo == temp_paths[1]

    obj2 = AvatarIngestData(
        input_avatar=temp_paths[0],
        output_bgeo=temp_paths[1],
        output_gltf=temp_paths[2],
        output_thumbnail=temp_paths[3],
        output_skelref=temp_paths[4],
        input_mapping=temp_paths[5]) # with path too

    assert obj2.input_mapping == temp_paths[5]
