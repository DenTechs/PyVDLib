import mmap
import struct
import numpy as np
import time
from dataclasses import dataclass
import math

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
    Align(4)
    return struct.unpack('f', mm.read(4))[0]

def ReadUint32():
    Align(4)
    return struct.unpack('L', mm.read(4))[0]
    
def ReadUint64():
    Align(8)
    return struct.unpack('Q', mm.read(8))[0]

def ReadVector3():
    Align(4)
    UnpackedPose = struct.unpack("fff", mm.read(12))
    return Vector3(UnpackedPose[0], UnpackedPose[1], UnpackedPose[2])

def ReadPose():
    Align(4)
    UnpackedPose = struct.unpack("fffffff", mm.read(28))
    return Pose(Quaternion(UnpackedPose[0],UnpackedPose[1],UnpackedPose[2],UnpackedPose[3]), Vector3(UnpackedPose[4], UnpackedPose[5], UnpackedPose[6]))

def ReadFingerJointState():
    return FingerJointState(Pose=ReadPose(), Radius=ReadFloat(), AngularVelocity=ReadVector3(), LinearVelocity=ReadVector3())

def ReadHandTrackingAimState():
    handTrackingAimStateRead = HandTrackingAimState(AimStatus=ReadUint64(), AimPose=ReadPose(), PinchStrengthIndex=ReadFloat(), PinchStrengthMiddle=ReadFloat(), PinchStrengthRing=ReadFloat(), PinchStrengthLittle=ReadFloat())
    Align(8)
    return handTrackingAimStateRead

def ReadBodyJointLocation():
    bodyJointLocationRead = BodyJointLocation(LocationFlags=ReadUint64(), Pose=ReadPose())
    Align(8)
    return bodyJointLocationRead

def ReadSkeletonJoints():
    return SkeletonJoint(Joint=ReadUint32(), ParentJoint=ReadUint32(), Pose=ReadPose())

def Align(alignAmount: int):
    while mm.tell() % alignAmount != 0:
        mm.seek(1,1)

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

while True:
    mm = mmap.mmap(-1, 9788,"VirtualDesktop.BodyState")

    FaceIsValid = ReadBool()

    IsEyeFollowingBlendshapesValid = ReadBool()

    ExpressionWeights = np.empty(ExpressionCount, dtype=float)
    i = 0
    while i < ExpressionWeights.size:
        ExpressionWeights[i] = ReadFloat()
        i+=1
    
    ExpressionConfidences = np.empty(ConfidenceCount, dtype=float)
    i = 0
    while i < ExpressionConfidences.size:
        ExpressionConfidences[i] = ReadFloat()
        i+=1

    LeftEyeIsValid = ReadBool()
    RightEyeIsValid = ReadBool()

    LeftEyePose = ReadPose()
    RightEyePose = ReadPose()

    # pose = euler_from_quaternion(LeftEyePose.Orientation.x,LeftEyePose.Orientation.y,LeftEyePose.Orientation.z,LeftEyePose.Orientation.w)
    # print(f"X: {round(pose[0],4)}\nY: {round(pose[1],4)}\nZ: {round(pose[2],4)}\n")

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

    mm.close()

    time.sleep(0.25)
    #break





