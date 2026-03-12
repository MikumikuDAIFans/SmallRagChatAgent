## running jobs
This chapter willguide users through the complete machining process from device connection to carving
completion,ensuring safe and efficient operation.The example focuses on CNC carving; laser carving users
can skip Installing the Toolhead and Tool Calibration.
## Connect the Device
Connect the carving device to the computer via USB,ensuring the driver is correctly installed (see driver-setup)
and the device status is normal. Once connected successfully, the "Device" area on the right side of the
ArtiMaker page will display device information, as shown below:

## Confirm Material Size
It is recommended that the material size be slightly smaller than the maximum machining range of the device,
eavingspaceorclampstoscurtmatrahisprevntssafthazardscausdbimprperfixatinde
to oversized material.
## Secure the Material
n
Use clamps to firmly secure the material on the worktable,ensuring it does notshift or vibrate during
machining,which could affect carving accuracy.
## Install the Toolhead
Selecttheappropriatetoolbasedonmachiningneeds(eg,flatendmilballendmillV-bit,andinstalli
correctlyonthespindle.Ensure it istightenedsecurelytoavoidlooseningduring machining.
## Tool Calibration
Use the Jog buttons (X-,X+,Y-,Y+) or manually move X and Y to position the toolhead appropriately,usually at
helowerltceoftmatrauprbtcalbataxmakipcto
the material surface to ensure accurate carving depth.

## Set the Zero Point
As shown in theinterface,set the machiningorigin in the Start Carving interfaceby clicking ResetxY and
ResetZ.

## Frame
To ensure machining safety and path accuracy, it is recommended to perform a Frame operation before
officially starting carving.
Click the "Frame" button as shown below, and ArtiMaker will drive the CNC device along the boundary
trajectoryof thecarving task,simulating the tool's movementrange.This allowsusers to confirm whether the
material position is correct, clamps interfere, and make timely adjustments to avoid machining errors or

## Start Carving
Click the "Run" button as shown below to start the machining task.The device willautomatically execute the
carvingoperationaccording to thegenerated toolpathUserscanmonitorprogressanddevicestatusin real time during machining to ensure smooth execution.

cabgvidiaowdtdt
1. Estimated Time: Predicted machining duration calculated from the toolpath
2.Remaining Time: Remaining machining time for the current task
3.Carving Progress: Task completion percentage
4.Device Status and Position: Real-time display of tool coordinates and device status