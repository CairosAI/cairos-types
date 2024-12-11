import pytest
from pathlib import Path

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
def existing_file() -> Path:
    return Path(Path(__file__).parent.parent.parent , 'pyproject.toml')

@pytest.fixture(scope='module')
def sequencer_avatar_data(existing_file: Path) -> SequencerAvatarData:
    return SequencerAvatarData(
        filepath=existing_file,
        output_bgeo=Path(__file__), # random paths, they do not matter now, and
                                    # are not validated at this stage, they are
                                    # here so the LSP does not complain about
                                    # missing parameters
        output_gltf=Path(__file__)
    )

@pytest.fixture(scope='module')
def mock_motions_list() -> list:
    return ['running', 'jumping']

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

    # get the names of its fields
    fields = sequencer_data.btl_list_fields()

    # here we check that the values in the field match with the ones we set, but
    # in a real use case we would just set a detai attribute on some
    # `hou.Geometry` with name `name` and value `attr_value.dict()` or
    # `attr_value.json()` (remember, `attr_value` is supposed to be a Pydantic
    # model)
    
    for name in fields:
        attr_value = getattr(sequencer_data, name)
        if name == 'avatar':
            assert attr_value == sequencer_avatar_data
        if name == 'animations':
            assert set(attr_value) <= set(mock_motions_list)