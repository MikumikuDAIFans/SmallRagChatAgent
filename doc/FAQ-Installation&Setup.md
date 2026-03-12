This document targets the current ArtiMaker frontend project and covers driver installation and updates, uninstall and troubleshooting, handling out-of-memory issues, and solutions for UI display anomalies.

- Target OS: Windows 10 or later (64-bit recommended)
- Recommended browsers: Chrome 90+, Firefox 88+, Edge 90+ (WebGL required)
- Enable browser hardware acceleration for better 3D performance

## How to Update the Driver to the Latest Version

ArtiMaker communicates with CNC/laser devices through a device driver.

### Update within the App

- Open the ArtiMaker web app (the Home top menu includes an “Install Driver” entry).
- After the device connects, the app receives version information and shows it in the G-code Console dialog from the top menu.

### Manual Update Procedure

1. Download the latest driver:
   - Driver documentation (Wiki): `https://wiki.artimaker.com/zh/appendix/download-center`
   - Direct download (Windows x64): `https://artimaker.com/download/ArtiMaker-Driver_windows-x64_V1_1.exe`
2. Right-click the installer and choose “Run as administrator”.
3. Complete installation as prompted.
4. Reopen ArtiMaker and connect the device to verify.

## How to Uninstall the Software

### Windows Control Panel

- Open “Control Panel” → “Programs and Features”.
- Find “ArtiMaker Driver”.
- Click “Uninstall” and follow the wizard.

### Windows Settings (Windows 10/11)

- Open “Settings” → “Apps”.
- Search for “ArtiMaker”.
- Select the driver entry → “Uninstall”.

### Complete Uninstall Checklist

- Restart the computer after uninstall.
- Confirm no ArtiMaker-related processes remain in Task Manager.
- Clear browser cache for the ArtiMaker site.

## Driver Installation Fails — What to Do

### Quick Fixes

- Run the installer with administrator privileges (right-click → “Run as administrator”).
- Temporarily disable antivirus/security software during installation.
- Add ArtiMaker to antivirus/firewall allowlists.
- Uninstall older driver versions before installing the new one.
- Restart the computer between uninstall and reinstall.

### System Checks

- Windows 10+ (64-bit recommended)
- Free disk space ≥ 500 MB
- Windows fully updated
- Close other CNC/3D printing software that might occupy serial/USB ports

### Port Conflicts

- Check Device Manager for port usage or anomalies.
- Close other applications using COM/USB ports.
- Replug the device, then try installation/connection again.

### If the Issue Persists

- Re-download the latest installer from the Install Driver link.
- Update system patches (Windows Update).
- Contact technical support with the error details and system environment.

## Out-of-Memory Errors

ArtiMaker involves 3D rendering and G-code parsing, which can consume substantial memory.

### Minimum Requirements

- Memory: ≥ 4 GB (≥ 8 GB recommended)
- Browser: Modern, WebGL-capable (Chrome, Firefox, Edge recommended)

### Optimization Tips

- Close unnecessary browser tabs and other applications.
- Clear browser cache.
- Enable hardware acceleration in browser settings.
- Simplify 3D models before import; reduce toolpath complexity (increase step size).
- Process large projects in segments.

### Recovery Steps

- Refresh the page after a memory error.
- Cancel long-running operations and execute in batches.
- Restart the browser and try again.

## UI Display Issues

### Browser Support

- Recommended: Chrome 90+, Firefox 88+, Edge 90+
- Supported: Safari 14+ (macOS; some behaviors may differ)
- Not supported: Internet Explorer

### Common Fixes

- Reset browser zoom to 100%.
- Reset system display scaling to 100%.
- Clear browser cache.
- Update graphics driver.
- Enable “Use hardware acceleration” in browser settings.

### Browser Feature Notes

- Ensure the browser allows file downloads and pop-ups; otherwise related buttons may not work.

---

- Submit issues via the feedback portal in the user center. Include your operating system and browser, device model, connection method, and any prompts shown when the issue occurred.
