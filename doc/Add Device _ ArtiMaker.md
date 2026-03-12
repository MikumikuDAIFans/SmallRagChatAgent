* * Add Device

    ArtiMaker supports connecting to CNC machines via USB serial ports. This section guides users on how to add, connect, and manage devices.

    ## Connection Steps

    **1. Hardware Connection**
    Connect the device to the computer via a USB cable. Ensure the machine is powered on.

    **2. Open Device List**
    Click the **Device** button in the top menu bar (icon resembling a plug).

    > **[Visual Description - Top Menu Bar]**
    > The image shows the top right corner of the ArtiMaker interface.
    > * There is a **"Device"** button with a plug icon.
    > * Adjacent buttons include "Setting" (gear icon) and window controls (minimize, maximize, close).

    **3. Select Port**
    The "Device List" window will pop up. The system automatically scans for available serial ports.
    * Select the correct port from the list (e.g., `COM3`).
    * If the device is not found, click the **Refresh** button.

    > **[Visual Description - Device List Window (Disconnected State)]**
    > A pop-up window titled **"Device List"** is displayed.
    > * **Device List:** A list item is visible showing the port name (e.g., `COM3`) and the driver description (e.g., `Silicon Labs CP210x USB to UART Bridge`).
    > * **Action Button:** A blue **"Connect"** button is located to the right of the device name.
    > * **Refresh:** A refresh icon (circular arrows) is positioned next to the "Device List" title to rescan ports.
    > * **Help Link:** A text link "No device found?" is available at the bottom for troubleshooting.

    **4. Connect**
    Click the **Connect** button behind the corresponding port. Once connected, the button status changes to **Disconnect**, and a green dot appears indicating a successful connection.

    > **[Visual Description - Device List Window (Connected State)]**
    > The interface shows the **"Device List"** window after a successful connection.
    > * **Status Indicator:** A green dot is visible next to the device name (`COM3`), indicating the "Connected" state.
    > * **Action Button:** The button has changed from a blue "Connect" button to a red **"Disconnect"** button.
    > * **Device Info:** The specific driver details (`Silicon Labs CP210x...`) remain visible.

    ---

    ## Troubleshooting

    If the device cannot be found or connected:
    * **Check Cable:** Ensure the USB cable is intact and firmly connected.
    * **Check Power:** Ensure the CNC machine is powered on.
    * **Install Driver:** If the computer does not recognize the serial port, you may need to install the CH340 or CP210x driver.
    * **Permission:** On macOS/Linux, ensure the user has permission to access the serial port.