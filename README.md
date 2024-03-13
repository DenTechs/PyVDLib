# PyVDLib

A library to make it easy to use the body tracking information from Virtual Desktop in Python

## Installation

PyVDLib can be installed with `pip install pyvdlib` and imported with `import PyVDLib`

## Usage

`AwaitVirtualDesktopSyncEvent(timeout)`
- timeout (optional) The duration in milliseconds to wait before timing out (default is 1000 ms).

Performs a blocking wait, halting the execution until an update is received from Virtual Desktop's event synchronization pulse, or until the specified timeout duration is reached.

`GetVirtualDesktopBodyDict()`

Returns a dict with the following keys:

- FaceIsValid (bool)
- IsEyeFollowingBlendshapesValid (bool)
- ExpressionWeights (dict of 70 floats, keys from 0-69)
- ExpressionConfidences (dict of 2 floats, keys from 0-1)
- LeftEyeIsValid (bool)
- RightEyeIsValid (bool)
- LeftEyePose (pose)
- RightEyePose (pose)
- LeftEyeConfidence (float)
- RightEyeConfidence (float)
- LeftHandActive (bool)
- RightHandActive (bool)
- LeftHandJointStates (dict of 26 FingerJointState's, keys from 0-25)
- RightHandJointStates (dict of 26 FingerJointState's, keys from 0-25)
- LeftAimState (HandTrackingAimState)
- RightAimState (HandTrackingAimState)
- BodyTrackingCalibrated (bool)
- BodyTrackingHighFidelity (bool)
- BodyTrackingConfidence (float)
- BodyJoints (dict of 84 BodyJointLocation's, keys from 0-83)
- SkeletonJoints (dict of 84 SkeletonJoints's, keys from 0-83)
- SkeletonChangedCount (Uint32)

### Quaternion
`x: float`
`y: float`
`z: float`
`w: float`

### Vector3
`x: float`
`y: float`
`z: float`

### Pose
`Orientation: Quaternion`
`Position: Vector3`

### FingerJointState
`Pose: Pose`
`Radius: float`
`AngularVelocity: Vector3`
`LinearVelocity: Vector3`

### HandTrackingAimState
`AimStatus: np.uint64`
`AimPose: Pose`
`PinchStrengthIndex: float`
`PinchStrengthMiddle: float`
`PinchStrengthRing: float`
`PinchStrengthLittle: float`

### BodyJointLocation
`LocationFlags: np.uint64`
`Pose: Pose`

Location flags function similarly to a boolean, but instead of being 0 or 1, they are either 0 or 15. These flags include bits for position and orientation, as well as a valid and tracked bit. As it currently stands, these are either all activated or all deactivated.

### SkeletonJoint
`Joint: np.uint32`
`ParentJoint: np.uint32`
`Pose: Pose`

List of joint mappings can be found here: [LINK](https://developer.oculus.com/documentation/unity/move-body-tracking/)