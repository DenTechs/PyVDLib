ExpressionCount = 70
ConfidenceCount = 2
HandJointCount = 26
FullBodyJointCount = 84


format = ""

format += "?" #FaceIsValid,
format += "?" #IsEyeFollowingBlendshapesValid

i=0
while i < ExpressionCount: #ExpressionWeights
    format += "f"
    i+=1

i=0
while i < ConfidenceCount: #ExpressionConfidences
    format += "f"
    i+=1

format += "?" #LeftEyeIsValid
format += "?" #RightEyeIsValid

format += "fffffff" #LeftEyePose (4f quat, 3f vector3)
format += "fffffff" #RightEyePose (4f quat, 3f vector3)

format += "f" #LeftEyeConfidence
format += "f" #RightEyeConfidence

format += "?" #RightEyeConfidence
format += "?" #RightEyeConfidence

i=0
while i < HandJointCount: #LeftHandJointStates
    format += "fffffff" + "f" + "fff" + "fff" #Pose + Radius + AngularVelocity + LinearVelocity
    i+=1

i=0
while i < HandJointCount: #RightHandJointStates
    format += "fffffff" + "f" + "fff" + "fff" #Pose + Radius + AngularVelocity + LinearVelocity
    i+=1  


format += "Q" + "fffffff" + "f" + "f" + "f" + "f" #LeftAimState AimStatus + AimPose + PinchStrengthIndex + PinchStrengthMiddle + PinchStrengthRing + PinchStrengthLittle
format += "Q" + "fffffff" + "f" + "f" + "f" + "f" #RightAimState AimStatus + AimPose + PinchStrengthIndex + PinchStrengthMiddle + PinchStrengthRing + PinchStrengthLittle

format += "?" #BodyTrackingCalibrated
format += "?" #BodyTrackingHighFidelity

format += "f" #BodyTrackingConfidence

i=0
while i < FullBodyJointCount: #BodyJoints
    format += "Q" + "fffffff" #BodyJointLocation LocationFlags + Pose
    i+=1

i=0
while i < FullBodyJointCount: #SkeletonJoints
    format += "L" + "L" + "fffffff" #SkeletonJoint Joint + ParentJoint + Pose
    i+=1

format += "L" #SkeletonChangedCount

print(f"\n\n{format}\n\n")

f = open("format_specifier.txt", "w")
f.write(format)
f.close()