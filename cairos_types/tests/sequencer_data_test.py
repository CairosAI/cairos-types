import pytest
import tempfile
from typing import Generator, Any
from cairos_types.core import Motion, Motions
from pathlib import Path

from cairos_types.houdini import SequencerAvatarData, SequencerDataWrapper

@pytest.fixture(scope='module')
def temp_paths() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".bgeo") as avatar, tempfile.NamedTemporaryFile(suffix=".bgeo.sc") as bgeo, tempfile.NamedTemporaryFile(suffix=".glb") as glb:
        yield [Path(avatar.name), Path(bgeo.name), Path(glb.name)]


@pytest.fixture(scope='module')
def motions(temp_paths: list[Path]) -> list[Motion]:

    data = [
        {
            "description": "Sneaky Look Around take 02",
            "input": str(temp_paths[0]),
            "tags": ["Sneaky", "Look", "Around", "take", "02"],
            "sg_id": 1,
            "shot_description": "Sneaking session",
            "created_at": "2025-06-09T00:00:00"
        },
        {
            "description": "Sneaky Look Around take 06",
            "input": str(temp_paths[1]),
            "tags": ["Sneaky", "Look", "Around", "take", "06"],
            "sg_id": 1,
            "shot_description": "Sneaking session",
            "created_at": "2025-06-09T00:00:00"
        }
    ]

    motions = list(map(lambda m: Motion(**m), data))
    return motions

@pytest.fixture(scope='module')
def avatar_data(temp_paths: list[Path]) -> SequencerAvatarData:
    return SequencerAvatarData(
        input=temp_paths[0],
        output_bgeo=temp_paths[1],
        output_gltf=temp_paths[2])

def test_sequencer_data(motions: list[Motion],
                        avatar_data: SequencerAvatarData):
    data = SequencerDataWrapper(
        avatar=avatar_data,
        animations=motions).convert_animations_to_hou_format()

    assert isinstance(data["animations"], dict)
    for key, value in data["animations"].items():
        assert isinstance(value, list)
