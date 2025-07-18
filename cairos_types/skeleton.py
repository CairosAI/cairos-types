from pydantic.v1 import BaseModel

# This is a class that represents a mapping of a user skeleton to our work
# skeleton. Each attribute is a joint in the skeleton and its value represents
# the corresponding joint in the user skeleton. Values may be the empty string,
# in which case there is no corresponding joint in the user skeleton.
class CairosWorkSkelMapping(BaseModel):
    LeftHandPalm: str
    LeftHandPinky1: str
    LeftHandPinky2: str
    LeftHandPinky3: str
    LeftHandRing1: str
    LeftHandRing2: str
    LeftHandRing3: str
    LeftHandMid1: str
    LeftHandMid2: str
    LeftHandMid3: str
    LeftHandIndex1: str
    LeftHandIndex2: str
    LeftHandIndex3: str
    LeftHandThumb1: str
    LeftHandThumb2: str
    LeftHandThumb3: str
    RightHandPalm: str
    RightHandRing1: str
    RightHandRing2: str
    RightHandRing3: str
    RightHandMid1: str
    RightHandMid2: str
    RightHandMid3: str
    RightHandThumb1: str
    RightHandThumb2: str
    RightHandThumb3: str
    RightHandIndex1: str
    RightHandIndex2: str
    RightHandIndex3: str
    RightHandPinky1: str
    RightHandPinky2: str
    RightHandPinky3: str
    Reference: str
    Hips: str
    RightUpLeg: str
    RightLeg: str
    RightFoot: str
    RightToeBase: str
    LeftUpLeg: str
    LeftLeg: str
    LeftFoot: str
    LeftToeBase: str
    Spine: str
    Spine1: str
    Spine2: str
    Spine3: str
    LeftShoulder: str
    LeftArm: str
    LeftForeArm: str
    RightShoulder: str
    RightArm: str
    RightForeArm: str
    Neck: str
    Head: str
