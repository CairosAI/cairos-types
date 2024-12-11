import pytest
from cairos_types.core import Motion, Motions
from pathlib import Path

from cairos_types.houdini import SequencerAvatarData, SequencerDataWrapper

@pytest.fixture(scope='module')
def existing_path() -> Path:
    return Path(Path(__file__).parent.parent.parent, 'pyproject.toml')

@pytest.fixture(scope='module')
def motions(existing_path: Path) -> list[Motion]:
    
    data = [
        {
            "action": "Sneaky Look Around take 02",
            "filepath": str(existing_path),
            "tags": ["Sneaky", "Look", "Around", "take", "02"],
            "sg_id": 1
        },
        {
            "action": "Sneaky Look Around take 06",
            "filepath": str(existing_path),
            "tags": ["Sneaky", "Look", "Around", "take", "06"],
            "sg_id": 1
        }
    ]

    motions = list(map(lambda m: Motion(**m), data))
    return motions

@pytest.fixture(scope='module')
def avatar_data(existing_path: Path) -> SequencerAvatarData:
    return SequencerAvatarData(
        input=existing_path,
        output_bgeo=Path('some/path.bgeo'),
        output_gltf=Path('some/path.gltf'))

def test_sequencer_data(motions: list[Motion],
                        avatar_data: SequencerAvatarData):
    data = SequencerDataWrapper(
        avatar=avatar_data,
        animations=motions)

    assert isinstance(data.animations, dict)
    for key, value in data.animations.items():
        assert isinstance(value, list)