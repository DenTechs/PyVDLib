import mmap
import struct
import numpy as np
import time
from dataclasses import dataclass

@dataclass
class Quaternion:
    x: float
    y: float
    z: float
    w: float

@dataclass
class Vector3:
    x: float
    y: float
    z: float

@dataclass
class Pose:
    Orientation: Quaternion
    Position: Vector3

@dataclass
class FingerJointState:
    Pose: Pose
    Radius: float
    AngularVelocity: Vector3
    LinearVelocity: Vector3

@dataclass
class HandTrackingAimState:
    AimStatus: np.uint64
    AimPose: Pose
    PinchStrengthIndex: float
    PinchStrengthMiddle: float
    PinchStrengthRing: float
    PinchStrengthLittle: float

@dataclass
class BodyJointLocation:
    LocationFlags: np.uint64
    Pose: Pose

@dataclass
class SkeletonJoint:
    Joint: np.uint32
    ParentJoint: np.uint32
    Pose: Pose

ExpressionCount = 70
ConfidenceCount = 2
HandJointCount = 26
FullBodyJointCount = 84

def ReadBool():
    return struct.unpack('?', mm.read(1))[0]

def ReadFloat():
    return struct.unpack('f', mm.read(4))[0]

def ReadUint32():
    return struct.unpack('L', mm.read(4))[0]
    
def ReadUint64():
    return struct.unpack('Q', mm.read(8))[0]

def ReadQuaternion():
    return Quaternion(x=ReadFloat(),y=ReadFloat(),z=ReadFloat(),w=ReadFloat())

def ReadVector3():
    return Vector3(x=ReadFloat(),y=ReadFloat(),z=ReadFloat())

def ReadPose():
    #return Pose(Orientation=ReadQuaternion(), Position=ReadVector3())
    #return Pose(Orientation=Quaternion(x=struct.unpack('f', mm.read(4))[0],y=struct.unpack('f', mm.read(4))[0],z=struct.unpack('f', mm.read(4))[0],w=struct.unpack('f', mm.read(4))[0]), Position=Vector3(x=struct.unpack('f', mm.read(4))[0],y=struct.unpack('f', mm.read(4))[0],z=struct.unpack('f', mm.read(4))[0]))
    struct.unpack("fffffff", mm.read(28))[0]

def ReadFingerJointState():
    return FingerJointState(Pose=ReadPose(), Radius=ReadFloat(), AngularVelocity=ReadVector3(), LinearVelocity=ReadVector3())

def ReadHandTrackingAimState():
    return HandTrackingAimState(AimStatus=ReadUint64(), AimPose=ReadPose(), PinchStrengthIndex=ReadFloat(), PinchStrengthMiddle=ReadFloat(), PinchStrengthRing=ReadFloat(), PinchStrengthLittle=ReadFloat())

def ReadBodyJointLocation():
    return BodyJointLocation(LocationFlags=ReadUint64(), Pose=ReadPose())

def ReadSkeletonJoints():
    return SkeletonJoint(Joint=ReadUint32(), ParentJoint=ReadUint32(), Pose=ReadPose())



file = open("format_specifier.txt", "r")
format = file.read()
file.close()


while True:
    mm = mmap.mmap(-1, 9432,"VirtualDesktop.BodyState")

    unpacked = struct.unpack(format, mm.read)





    FaceIsValid = ReadBool()

    IsEyeFollowingBlendshapesValid = ReadBool()

    ExpressionWeights = np.empty(ExpressionCount, dtype=float)
    i = 0
    while i < ExpressionWeights.size:
        ExpressionWeights[i] = ReadFloat()
        i+=1
    
    ExpressionConfidences = np.empty(2, dtype=float)
    i = 0
    while i < ExpressionConfidences.size:
        ExpressionConfidences[i] = ReadFloat()
        i+=1

    LeftEyeIsValid = ReadBool()
    RightEyeIsValid = ReadBool()

    LeftEyePose = ReadPose()
    RightEyePose = ReadPose()

    LeftEyeConfidence = ReadFloat()
    RightEyeConfidence = ReadFloat()

    LeftHandActive = ReadBool()
    RightHandActive = ReadBool()

    LeftHandJointStates = np.empty(HandJointCount, dtype=FingerJointState)
    i = 0
    while i < LeftHandJointStates.size:
        LeftHandJointStates[i] = ReadFingerJointState()
        i+=1

    RightHandJointStates = np.empty(HandJointCount, dtype=FingerJointState)
    i = 0
    while i < RightHandJointStates.size:
        RightHandJointStates[i] = ReadFingerJointState()
        i+=1

    LeftAimState = ReadHandTrackingAimState()
    RightAimState = ReadHandTrackingAimState()

    BodyTrackingCalibrated = ReadBool()
    BodyTrackingHighFidelity = ReadBool()
    BodyTrackingConfidence = ReadFloat()

    BodyJoints = np.empty(FullBodyJointCount, dtype=BodyJointLocation)
    i = 0
    while i < BodyJoints.size:
        BodyJoints[i] = ReadBodyJointLocation()
        i+=1

    SkeletonJoints = np.empty(FullBodyJointCount, dtype=SkeletonJoint)
    i = 0
    while i < SkeletonJoints.size:
        SkeletonJoints[i] = ReadSkeletonJoints()
        i+=1

    SkeletonChangedCount = ReadUint32()

    print(LeftHandActive)

    mm.close()

    time.sleep(0.1)
    #break





