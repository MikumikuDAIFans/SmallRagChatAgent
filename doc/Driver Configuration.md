> * Driver Configuration
>
>   ArtiMaker is compatible with standard GRBL firmware. Users can modify internal parameters of the motherboard (such as pulse, acceleration, stroke) via the **Machine Settings** interface to adapt to different hardware structures.
>
>   ## Accessing Configuration
>
>   **1. Connect Device**
>   Ensure the computer is connected to the machine (see "Add Device").
>
>   **2. Enter Settings**
>   Click the **Settings** button in the top menu bar (gear icon).
>
>   > **[Visual Description - Top Menu]**
>   > The image shows the top right corner of the interface.
>   > * The **"Settings"** button (gear icon) is highlighted.
>   > * It is located next to the "Device" (plug icon) button.
>
>   **3. Select Tab**
>   Switch to the **Machine Setup** tab in the settings window.
>
>   > **[Visual Description - Settings Window]**
>   > A window titled **"Settings"** is open.
>   > * The left sidebar lists three tabs: **General**, **Machine Setup**, and **About**.
>   > * The **"Machine Setup"** tab is currently selected (highlighted in blue).
>   > * The right panel displays configuration categories like "Travel Resolution" and "Max Rate".
>
>   ---
>
>   ## Parameter Description
>
>   The configuration list corresponds to standard GRBL `$` commands. Common parameters include:
>
>   ### 1. Travel Resolution (Steps/mm)
>   * **$100 (X-axis), $101 (Y-axis), $102 (Z-axis)**
>   * **Description:** The number of pulses required for the motor to move 1 millimeter.
>   * **Calculation Formula:** `(360 / Step Angle) * Microsteps / Pitch`
>
>   > **[Visual Description - Travel Resolution Settings]**
>   > The image details the "Travel Resolution" section.
>   > * **X-axis ($100):** Input field showing value `80.000` step/mm.
>   > * **Y-axis ($101):** Input field showing value `80.000` step/mm.
>   > * **Z-axis ($102):** Input field showing value `80.000` step/mm.
>   > * Each field has a numeric input box and a unit label "step/mm".
>
>   ### 2. Max Rate (mm/min)
>   * **$110 (X), $111 (Y), $112 (Z)**
>   * **Description:** The maximum moving speed of the axis. If set too high, the motor may stall.
>
>   > **[Visual Description - Max Rate Settings]**
>   > The image shows the "Max Rate" section.
>   > * **X-axis ($110):** Input field showing value `1000.000` mm/min.
>   > * **Y-axis ($111):** Input field showing value `1000.000` mm/min.
>   > * **Z-axis ($112):** Input field showing value `1000.000` mm/min.
>
>   ### 3. Acceleration (mm/sec²)
>   * **$120 (X), $121 (Y), $122 (Z)**
>   * **Description:** The acceleration of the axis start/stop.
>
>   > **[Visual Description - Acceleration Settings]**
>   > The image shows the "Acceleration" section.
>   > * **X-axis ($120):** Value set to `30.000` mm/sec^2.
>   > * **Y-axis ($121):** Value set to `30.000` mm/sec^2.
>   > * **Z-axis ($122):** Value set to `30.000` mm/sec^2.
>
>   ### 4. Max Travel (mm)
>   * **$130 (X), $131 (Y), $132 (Z)**
>   * **Description:** The maximum stroke of the machine. Used for soft limit protection.
>
>   ### 5. Other Settings
>   * **$0 (Step Pulse):** Pulse width duration (microseconds).
>   * **$1 (Step Idle Delay):** Motor lock delay time (255 = keep locked).
>   * **$3 (Direction Port Invert):** Invert axis movement direction.
>   * **$20 (Soft Limits):** Enable/Disable software limit protection.
>   * **$21 (Hard Limits):** Enable/Disable hardware limit switches.
>   * **$22 (Homing Cycle):** Enable/Disable automatic homing.
>   * **$23 (Homing Dir Invert):** Invert homing direction.
>
>   ---
>
>   ## Modifying and Saving
>
>   **1. Modify Value**
>   Directly enter the new value in the input box corresponding to the parameter.
>
>   **2. Save**
>   After modification, click the **Apply** button at the bottom of the interface. The system will send the new parameters to the motherboard and save them.
>
>   > **[Visual Description - Save Action]**
>   > The bottom of the Settings window is shown.
>   > * A blue **"Apply"** button is visible in the bottom right corner.
>   > * A "Cancel" button is located to its left.
>
>   **3. Import/Export**
>   * **Import Profile:** Load a local `.cfg` configuration file.
>   * **Export Profile:** Save current settings as a local file for backup.
>
>   > **[Visual Description - Profile Management]**
>   > The image shows buttons for file management.
>   > * **Import Profile:** Button with an upward arrow/folder icon.
>   > * **Export Profile:** Button with a downward arrow/save icon.