# Editing & Transformation

ArtiMaker supports precise editing of drawn objects, including moving, scaling, rotating, aligning, and boolean operations.

## Basic Transformation

**1. Selection**
* Click an object to select it.
* Hold `Shift` and click multiple objects to perform **Multi-select**.
* Drag a selection box to select all objects within the area.

**2. Move**
* **Mouse Operation:** Drag the selected object directly to move it.
* **Parametric Operation:** Enter exact coordinates in the **X** and **Y** input boxes in the top property bar.

> **[Visual Description - Position Settings]**
> The image displays the position control section of the property bar.
> * **X:** Input field for the X-axis coordinate (e.g., `10.00`).
> * **Y:** Input field for the Y-axis coordinate (e.g., `10.00`).
> * A lock icon might be visible to lock position or aspect ratio.

**3. Scale**
* **Mouse Operation:** Drag the **control points** (eight blue squares) around the selected object. Dragging corner points scales proportionally; dragging side points stretches the object.
* **Parametric Operation:** Enter values in the **W** (Width) and **H** (Height) input boxes. Click the "Lock" icon between W and H to maintain the aspect ratio.

> **[Visual Description - Size Settings]**
> The image shows the size control section.
> * **W:** Input field for Width (e.g., `50.00`).
> * **H:** Input field for Height (e.g., `50.00`).
> * **Lock Icon:** A padlock icon indicating whether the aspect ratio is locked (closed) or unlocked (open).

**4. Rotate**
* **Mouse Operation:** Move the mouse to the **rotation handle** (usually a protruding point at the top of the selection box) until the cursor turns into a rotation icon, then drag.
* **Parametric Operation:** Enter the angle in the **Rotate** input box (unit: degrees).

---

## Alignment Tools

When multiple objects are selected, the alignment tools in the top toolbar become active.

**Alignment Functions:**
* **Align Left:** Align the left edges of all selected objects.
* **Align Horizontal Center:** Align the horizontal centers.
* **Align Right:** Align the right edges.
* **Align Top:** Align the top edges.
* **Align Vertical Center:** Align the vertical centers.
* **Align Bottom:** Align the bottom edges.

> **[Visual Description - Alignment Toolbar]**
> The image shows a row of icons representing alignment functions:
> * **Left:** A vertical line with bars aligned to its left.
> * **Center (H):** A vertical line with bars centered on it.
> * **Right:** A vertical line with bars aligned to its right.
> * **Top:** A horizontal line with bars aligned below it.
> * **Center (V):** A horizontal line with bars centered on it.
> * **Bottom:** A horizontal line with bars aligned above it.

---

## Boolean Operations

Boolean operations allow combining standard shapes to create complex geometries. Select **two or more** overlapping objects to use these tools.

**1. Union**
Merges selected objects into one single shape. The path outline is the perimeter of the combined shapes.

> **[Visual Description - Union Example]**
> The image shows two overlapping shapes (e.g., a circle and a rectangle).
> * **Before:** Two distinct outlines overlapping.
> * **After:** A single outline merging both shapes, with internal lines removed.

**2. Subtract (Difference)**
Uses the top object to cut the bottom object.
* **Order matters:** The object selected last (or on top layer) acts as the cutter.

> **[Visual Description - Subtract Example]**
> The image demonstrates the subtraction process.
> * **Result:** The shape of the top object is removed from the bottom object, creating a cutout or "bite" mark.

**3. Intersect**
Retains only the overlapping part of the selected objects.

> **[Visual Description - Intersect Example]**
> The image shows the result of intersection.
> * **Result:** Only the area where the two shapes overlapped remains; the rest is deleted.

---

## Other Tools

**1. Group / Ungroup**
* **Group:** Combines multiple objects into a single logical unit, ensuring their relative position remains unchanged during movement.
* **Ungroup:** Breaks a group back into individual editable objects.

**2. Offset**
Creates a new path expanding or contracting from the original object's outline.
* **Distance:** Positive value expands (outward), negative value contracts (inward).
* **Join Style:** Set corner style (Round, Miter, Bevel).