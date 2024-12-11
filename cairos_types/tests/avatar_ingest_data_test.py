from cairos_types.houdini import AvatarIngestData
import pytest
from pathlib import Path

@pytest.fixture(scope='module')
def existing_file() -> Path:
    return Path(Path(__file__).parent.parent.parent , 'pyproject.toml')

@pytest.fixture(scope='module')
def existing_dir(existing_file: Path) -> Path:
    return existing_file.parent

def test_avatar_ingest_data_creation(existing_file: Path,
                                     existing_dir: Path):
    obj = AvatarIngestData(input_path=existing_file,
                           output_path=existing_dir,
                           mapping='mixamo') # LSP does not complain, even
                                             # completion works

    assert isinstance(obj.mapping, Path)
    assert obj.input_path == existing_file
    assert obj.output_path == existing_dir

    obj2 = AvatarIngestData(input_path=existing_file,
                            output_path=existing_dir,
                            mapping=existing_file) # with path too

    assert obj2.mapping == existing_file
