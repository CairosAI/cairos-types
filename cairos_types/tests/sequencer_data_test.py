import pytest
import tempfile
from typing import Generator, Any
from cairos_types.core import Motion, Motions
from pathlib import Path

from cairos_types.houdini import SequencerAvatarData, SequencerDataWrapper

@pytest.fixture(scope='module')
def existing_path() -> Path:
    return Path(Path(__file__).parent.parent.parent, 'pyproject.toml')

@pytest.fixture(scope='module')
def temp_paths() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".bgeo") as bgeo, tempfile.NamedTemporaryFile(suffix=".glb") as glb:
        yield [Path(bgeo.name), Path(glb.name)]


@pytest.fixture(scope='module')
def motions(existing_path: Path) -> list[Motion]:

    data = [
        {
            "description": "Sneaky Look Around take 02",
            "input": str(existing_path),
            "tags": ["Sneaky", "Look", "Around", "take", "02"],
            "sg_id": 1
        },
        {
            "description": "Sneaky Look Around take 06",
            "input": str(existing_path),
            "tags": ["Sneaky", "Look", "Around", "take", "06"],
            "sg_id": 1
        }
    ]

    motions = list(map(lambda m: Motion(**m), data))
    return motions

@pytest.fixture(scope='module')
def avatar_data(existing_path: Path, temp_paths: list[Path]) -> SequencerAvatarData:
    return SequencerAvatarData(
        input=existing_path,
        output_bgeo=Path(temp_paths[0]),
        output_gltf=Path(temp_paths[1]))

def test_sequencer_data(motions: list[Motion],
                        avatar_data: SequencerAvatarData):
    data = SequencerDataWrapper(
        avatar=avatar_data,
        animations=motions)

    assert isinstance(data.animations, dict)
    for key, value in data.animations.items():
        assert isinstance(value, list)
