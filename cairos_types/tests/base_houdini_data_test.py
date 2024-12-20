import pytest
import json
from pathlib import Path
from typing import Generator, Any
import tempfile

from cairos_types.core import Motion
from cairos_types.houdini import SequencerAvatarData, SequencerDataWrapper, BaseHoudiniData

# This file explains the reasoning for `BaseHoudiniData` and showcases how it
# should be used. This class should be subclassed by other classes, which define
# data that will be used as input for Houdini jobs. Currently the convention is
# to set one or more detail attributes with dictionary values on a specified
# node in the Houdini scene. `BaseHoudiniData` allows you to compose several
# other types (that define the shapes of dictionaries in attribute value) and
# easily iterate over them with `BaseHoudiniData.btl_list_fields()`. This way
# each attribute of the data definition class can be translated to a detail
# attrib in Houdini.

# To illustrate the usage of `BaseHoudiniData` we need its subclass, in this
# example `SequencerData`

# prerequisites:

@pytest.fixture(scope='module')
def temp_paths() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".bgeo") as avatar,\
         tempfile.NamedTemporaryFile(suffix=".bgeo.sc") as bgeo, \
         tempfile.NamedTemporaryFile(suffix=".glb") as glb:
        yield [Path(avatar.name), Path(bgeo.name), Path(glb.name)]

@pytest.fixture(scope='module')
def temp_paths_motions() -> Generator[list[Path], Any, Any]:
    with tempfile.NamedTemporaryFile(suffix=".bgeo") as avatar, \
         tempfile.NamedTemporaryFile(suffix=".bgeo") as bgeo, \
         tempfile.NamedTemporaryFile(suffix=".bgeo") as glb:
        yield [Path(avatar.name), Path(bgeo.name), Path(glb.name)]


@pytest.fixture(scope='module')
def sequencer_avatar_data(temp_paths: list[Path]) -> SequencerAvatarData:
    return SequencerAvatarData(
        input=temp_paths[0],
        output_bgeo=temp_paths[1], # random paths, they do not matter now, and
                                    # are not validated at this stage, they are
                                    # here so the LSP does not complain about
                                    # missing parameters
        output_gltf=temp_paths[2]
    )

@pytest.fixture(scope='module')
def mock_motions_list(temp_paths_motions: list[Path]) -> list:
    return [
        Motion(
            sg_id=123,
            description='running',
            input=str(temp_paths_motions[0]),
            tags=['a', 'b', 'c']),
        Motion(
            sg_id=345,
            description='jumping',
            input=str(temp_paths_motions[1]),
            tags=['d', 'e', 'f'])]

# SequencerData
@pytest.fixture(scope='module')
def sequencer_data(sequencer_avatar_data: SequencerAvatarData,
                   mock_motions_list: list) -> SequencerDataWrapper:
    return SequencerDataWrapper(
        avatar=sequencer_avatar_data,
        animations=mock_motions_list)

def test_base_houdini_data_conversion(sequencer_data: SequencerDataWrapper,
                                      sequencer_avatar_data: SequencerAvatarData,
                                      mock_motions_list: list):

    # Make sure that `sequencerData` is indeed a subclass of `BaseHoudiniData`
    assert issubclass(type(sequencer_data), BaseHoudiniData)
    sequencer_dict_data = sequencer_data.convert_animations_to_hou_format()

    assert sequencer_dict_data["avatar"] == \
        json.loads(sequencer_avatar_data.json())
    assert set(sequencer_dict_data["animations"].keys()) == \
        set(json.loads(mock_motions_list[0].json()).keys())
