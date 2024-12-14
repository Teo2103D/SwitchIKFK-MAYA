How it works: 
Works with a rig that has 3 IK FK SK joint chains.

Step 1: 
Find the IK joint chains. Select an IK joint chain in order (Shoulder -> Elbow -> Wrist for arms / Hip -> Knee -> Ankle for legs) and then place the basic locators (script: locIKFK). 
Repeat the action on Arm_L, Arm_R, Leg_L, and Leg_R.

Step 2: 
Now select the "FK_wrist" joint so the IK control can snap to it. Attention!!! 
With AdvanceSkeleton, the IK controls do not have the same pivot point as the joints. In this case: select your IK control, run the locIKFK script, then change the name of the Locator so that it is in IK mode, not FK. Then, delete the parent constraint and create a new parent constraint from the "FK_wrist" joint to your Locator.

Step 3: 
Select an FK joint chain and run the LocPV script. Repeat the action on all IK joint chains: Arm_L, Arm_R, Leg_L, and Leg_R.

Now, you can do whatever you want with the created locators, group them and store them in the rig group or wherever, just don’t delete them.

SwitchIkFk: 
The IK switch works only if 2 or 4 objects are selected. It is effective when the following controls are selected in this exact order: PV_ctrl -> IK_ctrl.

The FK switch works only if 3 or 6 objects are selected. It is effective when selected in the parent-to-child hierarchy order: Shoulder_ctrl -> Elbow_ctrl -> Wrist_ctrl / Hip_ctrl -> Knee_ctrl -> Ankle_ctrl.

Good animating :)
