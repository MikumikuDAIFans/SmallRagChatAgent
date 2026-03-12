# Importing

ArtiMaker supports importing various standard file formats, allowing users to load external design files into the canvas for editing or machining.

**Supported file formats include:**
* **Vector:** `.svg`, `.dxf`
* **Bitmap:** `.jpg`, `.jpeg`, `.png`, `.bmp`
* **G-code:** `.nc`, `.gcode`

---

## 1. Vector Files (.svg, .dxf)

Vector files are ideal for cutting and profiling tasks as they contain precise path information.

**Import Steps:**
1.  Click the **Import** button (Image icon) in the left toolbar.
2.  Select the `.svg` or `.dxf` file from the file dialog.
3.  The vector graphic is loaded onto the canvas.

**Processing Logic:**
* **Closed Paths:** Automatically identified as shapes (e.g., circles, rectangles).
* **Open Paths:** Identified as line segments or polylines.
* **Group:** If the file contains multiple objects, they are grouped by default upon import. You can **Ungroup** them to edit individually.

> **Image Summary:**
> The interface displays a vector graphic (a stylized leaf shape) being imported onto the canvas grid. The graphic consists of clean, sharp lines defined by mathematical paths rather than pixels.

---

## 2. Bitmap Files (.jpg, .png, .bmp)

Bitmap files are used for relief carving or image engraving. ArtiMaker provides a built-in "Image to G-code" generator.

**Import Steps:**
1.  Click the **Import** button.
2.  Select an image file (e.g., `logo.png`).
3.  The **Image Processing** window pops up.

### Image Processing Options

When importing a bitmap, you can choose how to process the image:

| Mode                   | Description                                                  | Application                 |
| :--------------------- | :----------------------------------------------------------- | :-------------------------- |
| **Grayscale (Relief)** | Converts pixel brightness to Z-height (White = High, Black = Low). | 3D Relief Carving           |
| **Threshold (B&W)**    | Converts image to black and white based on a threshold value. | Laser Engraving / V-Carving |
| **Dithering**          | Simulates gray levels using dot patterns.                    | Laser Photo Engraving       |
| **Outline (Trace)**    | Detects edges and converts them to vector paths.             | Profiling / Cutting         |

**Parameter Settings:**
* **Invert:** Inverts black and white (Negative).
* **Brightness / Contrast:** Adjusts image quality.
* **Size:** Sets the physical size of the imported image.

> **Image Summary:**
> A screenshot of the "Image Processing" dialog box. It shows a preview of a loaded image on the left and a control panel on the right. The control panel includes sliders for "Threshold", "Brightness", and "Contrast", and buttons for different processing modes like "Grayscale" and "Outline".

---

## 3. G-code Files (.nc, .gcode)

If you have already generated G-code using other CAM software (e.g., Fusion 360, ArtCAM, VCarve), you can import it directly into ArtiMaker for preview and sending to the machine.

**Import Steps:**
1.  Click **File > Import G-code** in the top menu bar.
2.  Select the `.nc` or `.gcode` file.
3.  The system automatically enters the **3D Preview** interface.

**Restrictions:**
* Imported G-code files **cannot be edited** (move, scale, rotate) on the canvas.
* You can only view the toolpath in the 3D Preview and click **Craft** to run it.

> **Image Summary:**
> The view shows the 3D Preview interface after importing a G-code file. Instead of editable shapes, the canvas displays a complex network of blue and red lines representing the tool movement paths (toolpaths) directly derived from the code. The "Generate Toolpath" button is likely disabled or replaced by "Craft".

---

## 4. Drag and Drop Import

ArtiMaker supports quick import via drag and drop.

* **Operation:** Directly drag the file from your computer's folder window onto the ArtiMaker canvas.
* The system will automatically recognize the file format and trigger the corresponding import flow.

> **Image Summary:**
> An illustration of the drag-and-drop action. A mouse cursor is shown dragging a file icon labeled "design.svg" from a desktop folder window into the open ArtiMaker software window.