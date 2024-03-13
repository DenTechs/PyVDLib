import mmap
import struct
import numpy as np
from dataclasses import dataclass
from win32 import win32event

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

MemoryMapName = "VirtualDesktop.BodyState"
BodyStateEventName = "VirtualDesktop.BodyStateEvent"

ExpressionCount = 70
ConfidenceCount = 2
HandJointCount = 26
FullBodyJointCount = 84

def ReadBool(mm: mmap.mmap):
    return struct.unpack('?', mm.read(1))[0]

def ReadFloat(mm: mmap.mmap):
    Align(mm, 4)
    return struct.unpack('f', mm.read(4))[0]

def ReadUint32(mm: mmap.mmap):
    Align(mm, 4)
    return struct.unpack('L', mm.read(4))[0]
    
def ReadUint64(mm: mmap.mmap):
    Align(mm, 8)
    return struct.unpack('Q', mm.read(8))[0]

def ReadVector3(mm: mmap.mmap):
    Align(mm, 4)
    UnpackedPose = struct.unpack("fff", mm.read(12))
    return Vector3(UnpackedPose[0], UnpackedPose[1], UnpackedPose[2])

def ReadPose(mm: mmap.mmap):
    Align(mm, 4)
    UnpackedPose = struct.unpack("fffffff", mm.read(28))
    return Pose(Quaternion(UnpackedPose[0],UnpackedPose[1],UnpackedPose[2],UnpackedPose[3]), Vector3(UnpackedPose[4], UnpackedPose[5], UnpackedPose[6]))

def ReadFingerJointState(mm: mmap.mmap):
    return FingerJointState(Pose=ReadPose(mm), Radius=ReadFloat(mm), AngularVelocity=ReadVector3(mm), LinearVelocity=ReadVector3(mm))

def ReadHandTrackingAimState(mm: mmap.mmap):
    handTrackingAimStateRead = HandTrackingAimState(AimStatus=ReadUint64(mm), AimPose=ReadPose(mm), PinchStrengthIndex=ReadFloat(mm), PinchStrengthMiddle=ReadFloat(mm), PinchStrengthRing=ReadFloat(mm), PinchStrengthLittle=ReadFloat(mm))
    Align(mm, 8)
    return handTrackingAimStateRead

def ReadBodyJointLocation(mm: mmap.mmap):
    bodyJointLocationRead = BodyJointLocation(LocationFlags=ReadUint64(mm), Pose=ReadPose(mm))
    Align(mm, 8)
    return bodyJointLocationRead

def ReadSkeletonJoints(mm: mmap.mmap):
    return SkeletonJoint(Joint=ReadUint32(mm), ParentJoint=ReadUint32(mm), Pose=ReadPose(mm))

def Align(mm: mmap.mmap, alignAmount: int):
    while mm.tell() % alignAmount != 0:
        mm.seek(1,1)

def AwaitVirtualDesktopSyncEvent(timeout = 1000):
    event_handle = win32event.OpenEvent(win32event.SYNCHRONIZE, False, BodyStateEventName)
    win32event.WaitForSingleObject(event_handle,timeout)

def GetVirtualDesktopBodyDict():
    dict = {}
    mm = mmap.mmap(-1, 9788, MemoryMapName)

    dict["FaceIsValid"] = ReadBool(mm)

    dict["IsEyeFollowingBlendshapesValid"] = ReadBool(mm)

    dict["ExpressionWeights"] = {}
    i = 0
    while i < ExpressionCount:
        dict["ExpressionWeights"][i] = ReadFloat(mm)
        i+=1
    
    dict["ExpressionConfidences"] = {}
    i = 0
    while i < ConfidenceCount:
        dict["ExpressionConfidences"][i] = ReadFloat(mm)
        i+=1

    dict["LeftEyeIsValid"] = ReadBool(mm)
    dict["RightEyeIsValid"] = ReadBool(mm)

    dict["LeftEyePose"] = ReadPose(mm)
    dict["RightEyePose"] = ReadPose(mm)

    dict["LeftEyeConfidence"] = ReadFloat(mm)
    dict["RightEyeConfidence"] = ReadFloat(mm)

    dict["LeftHandActive"] = ReadBool(mm)
    dict["RightHandActive"] = ReadBool(mm)

    dict["LeftHandJointStates"] = {}
    i = 0
    while i < HandJointCount:
        dict["LeftHandJointStates"][i] = ReadFingerJointState(mm)
        i+=1

    dict["RightHandJointStates"] = {}
    i = 0
    while i < HandJointCount:
        dict["RightHandJointStates"][i] = ReadFingerJointState(mm)
        i+=1

    dict["LeftAimState"] = ReadHandTrackingAimState(mm)
    dict["RightAimState"] = ReadHandTrackingAimState(mm)

    dict["BodyTrackingCalibrated"] = ReadBool(mm)
    dict["BodyTrackingHighFidelity"] = ReadBool(mm)
    dict["BodyTrackingConfidence"] = ReadFloat(mm)

    dict["BodyJoints"] = {}
    i = 0
    while i < FullBodyJointCount:
        dict["BodyJoints"][i] = ReadBodyJointLocation(mm)
        i+=1

    dict["SkeletonJoints"] = {}
    i = 0
    while i < FullBodyJointCount:
        dict["SkeletonJoints"][i] = ReadSkeletonJoints(mm)
        i+=1

    dict["SkeletonChangedCount"] = ReadUint32(mm)

    mm.close()

    return dict