# FAQ - Device Operation

This section provides solutions for common hardware connection, movement, and alarm status issues encountered during machine operation.

## Connection Issues

**Q: The software cannot find the serial port (COM port).**
* **Driver Missing:** You may need to install the serial port driver (CH340 or CP210x). Check your computer's "Device Manager" to see if there is an unrecognized device.
* **Cable Connection:** Ensure the USB cable is securely connected to both the computer and the control board. Try replacing the USB cable if necessary.
* **Power:** Ensure the CNC machine's power supply is turned on. Some boards require external power to be recognized.

**Q: I get a "Port Occupied" or "Access Denied" error when connecting.**
* **Other Software:** Check if another slicing or control software (e.g., Cura, LaserGRBL, LightBurn) is running and occupying the port. Close other software and try again.
* **Re-plug:** Unplug the USB cable and plug it back in to reset the port status.

> **[Visual Description - Connection Error]**
> The image illustrates a connection error message box or the Device List.
> * A warning icon (exclamation mark) might be visible next to the port selection.
> * The status indicator remains red or grey (Disconnected).

---

## Alarm & Status

**Q: The machine status is "ALARM". What should I do?**
The `ALARM` state usually indicates that the machine has triggered a limit switch or has been locked for safety.
* **Hard Limit:** The machine hit a physical limit switch. You need to reset the machine or manually move it away from the switch.
* **Soft Limit:** The requested move exceeded the maximum travel defined in settings ($130, $131, $132).
* **Solution:** Click the **Unlock** ($X) button in the Machine Control panel to clear the alarm state.

> **[Visual Description - Alarm and Unlock]**
> The image highlights the top status bar and control panel when an alarm occurs:
> * **State:** Displays `ALARM` in red text.
> * **Unlock Button:** A button with an "open padlock" icon is highlighted, indicating it must be clicked to restore the IDLE state.

**Q: What does "Hold" status mean?**
The `HOLD` state means the current task has been paused.
* **Cause:** User clicked "Pause", or the "Feed Hold" door switch was triggered.
* **Solution:** Click the **Resume** (Play icon) button to continue the job, or **Reset/Stop** to cancel.

---

## Movement & Homing

**Q: The axis moves in the opposite direction.**
* **Setting:** Go to **Settings > Machine Setup**.
* **Parameter:** Modify **$3 (Direction Port Invert)**. You need to calculate the mask value (bitmask) to invert specific axes (X, Y, or Z) and save the settings.

**Q: Homing cycle fails or moves the wrong way.**
* **Direction:** Check **$23 (Homing Dir Invert)** in Machine Settings to ensure the machine moves toward the limit switches during homing.
* **Switches:** Ensure the limit switches are properly connected and functioning. Check **$119 (Limit Switch Status)** via the console if available to verify triggering.

> **[Visual Description - Direction Settings]**
> The image shows the Machine Setup interface focusing on direction parameters:
> * **$3 Direction Port Invert:** A numeric input field or a set of toggle switches for X, Y, Z.
> * **$23 Homing Dir Invert:** Similar input for homing direction configuration.