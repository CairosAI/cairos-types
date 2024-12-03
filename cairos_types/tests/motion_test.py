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
        action='Running',
        filepath=str(existing_file),
        tags=[]
    )

    assert isinstance(m, Motion)


def test_motion_creation_sg_names(existing_file: Path):
    # the LSP will complain about this code since attributes with such names do
    # not exist on this class. Howerver this test will not fails, because the
    # `pre` validator will transform the keywords to match the names of the
    # defined attributes.
    m = Motion(
        id=1,
        description='Running',
        sg_file_animation=str(existing_file),
        tags=[]
    )

    assert isinstance(m, Motion)

    # The intended purpose of this mechanism is different - we receive
    # dictionaries with the following shape from the SG (FPTR) API:
    mock_sg_api_result = {
        'id': 1,
        'description': 'Running',
        'sg_file_animation': str(existing_file),
        'tags': []
    }

    # When we pass dict with kwargs to the `Motion` initializer we get no
    # complaints:
    m2 = Motion(**mock_sg_api_result)

    # Validation still works:
    assert isinstance(m2, Motion)

def test_motion_missing_file(nonexistent_file: Path):
    with pytest.raises(ValueError):
        m = Motion(
            sg_id=1,
            action='Running',
            filepath=str(nonexistent_file),
            tags=[])
