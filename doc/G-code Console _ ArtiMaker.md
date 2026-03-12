> # G-code Console
>
> The G-code Console provides a direct command-line interface for advanced users to communicate with the machine's controller (GRBL firmware). It allows for sending raw G-code commands and viewing real-time system feedback.
>
> ## Accessing the Console
>
> **1. Open Console**
> Click the **Console** button (icon resembling a command prompt `>_`) located in the bottom status bar or the top toolbar.
>
> **2. Interface Layout**
> The console window consists of two main areas:
> * **Log Area:** Display the history of sent commands and machine responses.
> * **Input Area:** A text box at the bottom for typing commands.
>
> ---
>
> ## Using the Console
>
> **Sending Commands**
> 1. Type a valid G-code or GRBL system command in the input box.
> 2. Press **Enter** on your keyboard or click the **Send** button.
> 3. The command will appear in the log, followed by the machine's response (usually `ok` if successful).
>
> **Viewing Status**
> The console automatically displays status reports when the machine is running or when requested.
> * **Information:** Coordinate positions, machine state (Idle, Run, Alarm), and error messages.
>
> ---
>
> ## Common Commands
>
> The console supports standard G-code and GRBL system commands. Here are some frequently used commands for troubleshooting:
>
> | Command  | Name             | Description                                                  |
> | :------- | :--------------- | :----------------------------------------------------------- |
> | **`$$`** | View Settings    | Lists all current configuration parameters ($0 - $132).      |
> | **`$#`** | View Coordinates | Displays the stored offsets for G54-G59 coordinate systems.  |
> | **`$G`** | View State       | Shows the active G-code modal states (e.g., G0, G54, G21).   |
> | **`$I`** | Build Info       | Displays the firmware version and build date.                |
> | **`$X`** | Kill Alarm       | Unlocks the machine from an ALARM state. Use with caution.   |
> | **`$H`** | Homing Cycle     | Forces the machine to run the homing sequence (if limit switches are installed). |
> | **`?`**  | Status Report    | Immediately queries the machine for its current status and position. |
>
> **Motion Commands:**
> * **`G0 X0 Y0`**: Rapidly move to the origin (0,0).
> * **`G1 Z5 F500`**: Move the Z-axis to 5mm at a speed of 500mm/min.