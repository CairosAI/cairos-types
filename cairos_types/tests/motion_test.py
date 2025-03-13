from pathlib import Path
from cairos_types.core import Motion
import pytest

@pytest.fixture(scope='module')
def existing_file() -> Path:
    return Path(Path(__file__).parent.parent.parent , 'pyproject.toml')

@pytest.fixture(scope='module')
def nonexistent_file() -> Path:
    return Path('/this_path_does/not/exist')

def test_motion_creation_field_names(existing_file: Path):
    m = Motion(
        sg_id=1,
        description='Running',
        input=str(existing_file))

    assert isinstance(m, Motion)

def test_motion_missing_file(nonexistent_file: Path):
    with pytest.raises(ValueError):
        _ = Motion(
            sg_id=1,
            description='Running',
            input=str(nonexistent_file))
