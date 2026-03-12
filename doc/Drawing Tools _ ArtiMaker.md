# Drawing Tools

ArtiMaker provides a rich set of 2D drawing tools, supporting the creation of basic shapes, lines, text, and importing external files.

## Toolbar Overview

The drawing toolbar is located on the left side of the canvas.

> **[Visual Description - Toolbar Layout]**
> The image displays a vertical toolbar on the left side of the interface containing icons for various tools:
> * **Select:** A cursor arrow icon.
> * **Circle:** A hollow circle icon.
> * **Rectangle:** A hollow rectangle icon.
> * **Polygon:** A hexagon icon.
> * **Star:** A five-pointed star icon.
> * **Line:** A diagonal line segment icon.
> * **Polyline:** A connected multi-segment line icon.
> * **Arc:** A curved line icon.
> * **Text:** A capital "T" icon.
> * **Image:** A picture/landscape icon.

---

## Tool Functions

### 1. Select
* **Function:** Used to select, move, scale, and rotate objects.
* **Operation:**
    * **Click:** Select a single object.
    * **Drag Frame:** Select multiple objects within the area.
    * **Transform:** Drag the control points of the selected object to scale or rotate it.

### 2. Circle
* **Function:** Draw a standard circle.
* **Operation:**
    * Click the left mouse button to determine the **center**.
    * Drag the mouse to determine the **radius**.
    * Click again to complete the drawing.

> **[Visual Description - Drawing a Circle]**
> The image illustrates the "Circle" tool in action on the grid canvas.
> * A center point is marked.
> * A blue outline of a circle expands as the cursor moves away from the center.
> * A radius line connects the center to the cursor position.

### 3. Rectangle
* **Function:** Draw a rectangle.
* **Operation:**
    * Click to determine the **start corner**.
    * Drag to the diagonal position to determine the **width and height**.
    * Click to complete.

> **[Visual Description - Drawing a Rectangle]**
> The image shows a blue rectangle being drawn on the canvas.
> * The starting corner is fixed.
> * The user is dragging the opposite corner to define the shape's size.
> * Dimensions (width/height) might be visible near the cursor.

### 4. Polygon
* **Function:** Draw a regular polygon (e.g., triangle, hexagon).
* **Operation:**
    * Set the **number of sides** (Sides) in the top property bar.
    * Click to determine the center and drag to determine the size.

> **[Visual Description - Polygon Settings]**
> The image highlights the top property bar when the Polygon tool is active.
> * An input field labeled "Sides" allows the user to enter a number (e.g., "5" or "6").

### 5. Star
* **Function:** Draw a star shape.
* **Operation:**
    * Set the **number of points** (Points) and **inner radius ratio** in the property bar.
    * Drag to draw.

### 6. Line
* **Function:** Draw a single straight line segment.
* **Operation:**
    * Click the **start point**.
    * Click the **end point**.

### 7. Polyline
* **Function:** Draw continuous line segments.
* **Operation:**
    * Click successively to determine multiple vertices.
    * **Right-click** to end the drawing.

> **[Visual Description - Drawing a Polyline]**
> The image shows a multi-segment line being created.
> * Several straight lines are connected at vertices.
> * The "rubber band" line follows the cursor to the next potential point.

### 8. Arc
* **Function:** Draw a circular arc.
* **Operation:**
    * Click the **start point**.
    * Click the **end point**.
    * Drag to adjust the **curvature** (radius) of the arc.

### 9. Text
* **Function:** Insert text objects.
* **Operation:**
    * Click on the canvas to place the text insertion point.
    * Enter text in the pop-up box.
    * Support setting **Font**, **Size**, and **Style** (Bold/Italic).

> **[Visual Description - Text Tool]**
> The image shows the Text input interface.
> * The word "ArtiMaker" is typed onto the canvas.
> * A settings panel is visible, offering options for "Font Family" (e.g., Arial), "Size", and toggle buttons for Bold (B) and Italic (I).

### 10. Image (Import)
* **Function:** Import external image files.
* **Supported Formats:**
    * **Bitmap:** JPG, PNG, BMP (Supports generating relief or gray-scale line paths).
    * **Vector:** SVG, DXF (Directly editable paths).
* **Operation:**
    * Click the Image tool.
    * Select a file from the local computer.
    * Click on the canvas to place it.

> **[Visual Description - Image Import]**
> The image demonstrates importing a file.
> * A file explorer window is open, showing image files (e.g., .png, .jpg).
> * The selected image is placed onto the canvas workspace.