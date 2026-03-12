# G-code Commands

## Motion Commands

### G0 - Rapid Positioning

**Syntax**: `G0 X[coordinate] Y[coordinate] Z[coordinate]`

**Function**: Move to the specified position at maximum speed without machining operations.

**Description**:

- Used for rapid positioning without cutting material
- Movement path may not be linear
- Displayed as red path in 3D visualization
- Automatically turns off laser in laser mode

**Examples**:

```gcode
G0 X10 Y20 Z5    ; Rapid move to (10, 20, 5)
G0 Z10           ; Z-axis only rapid move to 10mm
```

### G1 - Linear Interpolation

**Syntax**: `G1 X[coordinate] Y[coordinate] Z[coordinate] F[feed rate] S[laser power/spindle speed]`

**Function**: Move linearly to the target position at specified feed rate, can perform machining operations.

**Description**:

- Used for precise linear cutting or laser engraving
- Displayed as blue path in 3D visualization
- In laser mode, S parameter controls laser power
- In CNC mode, S parameter controls spindle speed

**Examples**:

```gcode
G1 X50 Y30 F1000      ; Move to (50,30) at 1000mm/min
G1 Z-2 F100 S800      ; Move down to Z-2, laser power 800
```

### G2 - Clockwise Arc Interpolation

**Syntax**: `G2 X[end X] Y[end Y] I[center X offset] J[center Y offset] F[feed rate]`

**Function**: Arc interpolation from current position to specified endpoint in clockwise direction.

**Description**:

- I, J parameters represent center offset relative to start point
- Currently treated as linear in visualization
- Suitable for arc cutting and engraving

**Examples**:

```gcode
G2 X20 Y20 I10 J0 F500    ; Clockwise arc to (20,20)
```

### G3 - Counterclockwise Arc Interpolation

**Syntax**: `G3 X[end X] Y[end Y] I[center X offset] J[center Y offset] F[feed rate]`

**Function**: Arc interpolation from current position to specified endpoint in counterclockwise direction.

**Description**:

- I, J parameters represent center offset relative to start point
- Currently treated as linear in visualization
- Suitable for arc cutting and engraving

**Examples**:

```gcode
G3 X0 Y20 I0 J10 F500     ; Counterclockwise arc to (0,20)
```

---

## Plane Selection Commands

### G17 - XY Plane Selection

**Syntax**: `G17`

**Function**: Select XY plane as working plane.

**Description**:

- Default working plane
- Arc interpolation performed in XY plane
- Z-axis is the vertical axis

### G18 - XZ Plane Selection

**Syntax**: `G18`

**Function**: Select XZ plane as working plane.

**Description**:

- Arc interpolation performed in XZ plane
- Y-axis is the vertical axis

### G19 - YZ Plane Selection

**Syntax**: `G19`

**Function**: Select YZ plane as working plane.

**Description**:

- Arc interpolation performed in YZ plane
- X-axis is the vertical axis

---

## Unit Setting Commands

### G20 - Inch Units

**Syntax**: `G20`

**Function**: Set coordinate units to inches.

**Description**:

- All subsequent coordinate values interpreted in inches
- 1 inch = 25.4 millimeters
- Affects all coordinates and feed rates

### G21 - Millimeter Units

**Syntax**: `G21`

**Function**: Set coordinate units to millimeters.

**Description**:

- Default unit setting
- All subsequent coordinate values interpreted in millimeters
- Recommended unit to use

---

## Homing and Reset Commands

### G28 - Return to Machine Home

**Syntax**: `G28` or `G28 X Y Z`

**Function**: Return to machine home position.

**Description**:

- Without parameters, all axes return to origin (0,0,0)
- With parameters, specified axes return to origin
- Current position set to (0,0,0) after execution

**Examples**:

```gcode
G28           ; All axes return to origin
G28 Z         ; Z-axis only return to origin
```

### G30 - Return to Preset Position

**Syntax**: `G30`

**Function**: Return to preset reference position.

**Description**:

- Similar to G28, but returns to preset position
- Specific position determined by machine configuration

### G92 - Set Current Position

**Syntax**: `G92 X[coordinate] Y[coordinate] Z[coordinate]`

**Function**: Set current position to specified coordinate values.

**Description**:

- Does not move machine, only redefines current position
- Used to establish workpiece coordinate system
- Affects all subsequent coordinate calculations

**Examples**:

```gcode
G92 X0 Y0 Z0    ; Set current position as origin
G92 X10         ; Set current X position to 10
```

---

## Pause Commands

### G4 - Dwell

**Syntax**: `G4 P[seconds]`

**Function**: Pause program execution for specified time.

**Description**:

- P parameter specifies pause time (seconds)
- Used for waiting spindle stabilization, cooling, etc.
- Does not change current position

**Examples**:

```gcode
G4 P2.5       ; Pause for 2.5 seconds
G4 P1         ; Pause for 1 second
```

---

## Coordinate Mode Commands

### G90 - Absolute Coordinate Mode

**Syntax**: `G90`

**Function**: Set to absolute coordinate mode.

**Description**:

- Default mode
- All coordinate values relative to workpiece origin
- Recommended coordinate mode

### G91 - Relative Coordinate Mode

**Syntax**: `G91`

**Function**: Set to relative coordinate mode.

**Description**:

- All coordinate values relative to current position
- Used for incremental movements
- Use with caution

---

## Coordinate System Selection Commands

### G53 - Machine Coordinate System

**Syntax**: `G53`

**Function**: Temporarily select machine coordinate system.

**Description**:

- Only effective for current line
- Coordinates relative to machine origin
- Often used with G0/G1

**Examples**:

```gcode
G0 G53 Z0     ; Z-axis return to 0 position in machine coordinate system
```

### G54-G59 - Workpiece Coordinate Systems

**Syntax**: `G54` / `G55` / `G56` / `G57` / `G58` / `G59`

**Function**: Select workpiece coordinate systems 1-6.

**Description**:

- G54 is default workpiece coordinate system
- Each coordinate system has independent origin offset
- Used for multi-workpiece machining

---

## Feed Rate Mode Commands

### G93 - Inverse Time Feed Mode

**Syntax**: `G93`

**Function**: Set inverse time feed mode.

**Description**:

- F value represents reciprocal of time required to complete the movement
- Less commonly used feed mode

### G94 - Units Per Minute Feed Mode

**Syntax**: `G94`

**Function**: Set units per minute feed mode.

**Description**:

- Default feed mode
- F value represents distance moved per minute
- Units: mm/min or inch/min

---

## Tool Compensation Commands

### G40 - Cancel Tool Compensation

**Syntax**: `G40`

**Function**: Cancel tool radius compensation.

**Description**:

- Default state
- Move precisely along programmed path

### G41 - Left Tool Compensation

**Syntax**: `G41`

**Function**: Enable left tool radius compensation.

**Description**:

- Tool center offset to left of programmed path
- Compensation value set by tool table

### G42 - Right Tool Compensation

**Syntax**: `G42`

**Function**: Enable right tool radius compensation.

**Description**:

- Tool center offset to right of programmed path
- Compensation value set by tool table

### G43 - Tool Length Compensation

**Syntax**: `G43`

**Function**: Enable tool length compensation.

**Description**:

- Compensate for tool length differences in Z-axis direction
- Compensation value set by tool table

### G49 - Cancel Tool Length Compensation

**Syntax**: `G49`

**Function**: Cancel tool length compensation.

**Description**:

- Return to uncompensated state
- Z-axis moves according to programmed values

---

## Canned Cycle Commands

### G80 - Cancel Canned Cycle

**Syntax**: `G80`

**Function**: Cancel current canned cycle.

**Description**:

- End cycle machining
- Return to normal movement mode

### G81 - Drilling Cycle

**Syntax**: `G81 X[position] Y[position] Z[depth] R[retract height] F[feed]`

**Function**: Execute simple drilling cycle.

**Description**:

- Rapid descent to R height
- Drill to Z depth at F speed
- Rapid retract to R height

### G82 - Drilling Cycle with Dwell

**Syntax**: `G82 X[position] Y[position] Z[depth] R[retract height] P[dwell time] F[feed]`

**Function**: Execute drilling cycle with dwell.

**Description**:

- Similar to G81, but dwell P seconds at bottom
- Used for chip breaking or chip evacuation

### G83 - Deep Hole Drilling Cycle

**Syntax**: `G83 X[position] Y[position] Z[depth] R[retract height] Q[peck feed] F[feed]`

**Function**: Execute peck drilling cycle.

**Description**:

- Multiple feed increments for deep holes
- Q parameter specifies feed increment per peck
- Retract for chip evacuation each time

---

## Spindle Control Commands

### M3 - Spindle On Clockwise/Laser On

**Syntax**: `M3 S[speed/power]`

**Function**: Start spindle clockwise rotation or turn on laser.

**Description**:

- CNC mode: S parameter is spindle speed (RPM)
- Laser mode: S parameter is laser power (0-1000)
- Must execute before cutting

**Examples**:

```gcode
M3 S12000     ; Spindle 12000 RPM
M3 S800       ; Laser power 800
```

### M4 - Spindle On Counterclockwise

**Syntax**: `M4 S[speed]`

**Function**: Start spindle counterclockwise rotation.

**Description**:

- Used for special machining requirements
- Such as tapping operations

### M5 - Spindle Stop/Laser Off

**Syntax**: `M5`

**Function**: Stop spindle or turn off laser.

**Description**:

- Safely stop spindle
- Turn off laser output in laser mode
- Must execute at end of machining

---

## Coolant Control Commands

### M7 - Mist Coolant On

**Syntax**: `M7`

**Function**: Turn on mist coolant.

**Description**:

- Used for light cooling
- Reduce dust

### M8 - Flood Coolant On

**Syntax**: `M8`

**Function**: Turn on flood coolant.

**Description**:

- Used for heavy cooling
- Improve machining quality

### M9 - Coolant Off

**Syntax**: `M9`

**Function**: Turn off all coolant.

**Description**:

- Stop coolant supply
- Execute at program end

---

## Program Control Commands

### M0 - Program Pause

**Syntax**: `M0`

**Function**: Pause program execution, wait for operator to continue.

**Description**:

- Requires manual continuation
- Used for workpiece inspection or tool change

### M1 - Optional Pause

**Syntax**: `M1`

**Function**: Optional program pause.

**Description**:

- Only effective when optional pause is enabled
- Used for program debugging

### M2 - Program End

**Syntax**: `M2`

**Function**: Program end.

**Description**:

- Stop spindle and coolant
- Program execution complete

### M30 - Program End and Return to Origin

**Syntax**: `M30`

**Function**: Program end and return to origin.

**Description**:

- Similar to M2, but automatically return to origin
- Recommended program end method

---

## Parameter Description

### Coordinate Parameters

- **X**: X-axis coordinate value
- **Y**: Y-axis coordinate value
- **Z**: Z-axis coordinate value
- **I**: Arc center X-axis offset
- **J**: Arc center Y-axis offset
- **K**: Arc center Z-axis offset

### Control Parameters

- **F**: Feed rate (mm/min or inch/min)
- **S**: Spindle speed (RPM) or Laser power (0-1000)
- **P**: Dwell time (seconds)
- **Q**: Peck feed amount (for cycles)
- **R**: Retract height (for cycles)

### Working Range Limits

- **X-axis**: -500mm to +500mm
- **Y-axis**: -500mm to +500mm
- **Z-axis**: -200mm to +200mm
- **Spindle Speed**: 0-24000 RPM
- **Laser Power**: 0-1000

### Comment Format

- Use semicolon ( ; ) to add comments
- Comment content does not affect program execution
- Recommend adding necessary explanations

**Examples**:

```gcode
G0 X0 Y0 Z5    ; Move to start position
M3 S800        ; Turn on laser, power 800
G1 X10 F1000   ; Linear move to X10
M5             ; Turn off laser
```
