# FAQ - Design & Files

This section addresses common questions regarding file formats, design preparation, and importing files into ArtiMaker.

## Supported File Formats

**Q: What file formats can I import into ArtiMaker?**
ArtiMaker supports both vector and raster (bitmap) files, as well as pre-generated G-code.

* **Vector Files:** `.svg`, `.dxf`
    * Best for: Cutting, profiling, and precise line work.
    * *Note:* Ensure text is converted to paths/curves before saving.
* **Raster Files:** `.jpg`, `.png`, `.bmp`
    * Best for: Relief carving, engraving, and heightmap generation.
* **G-code Files:** `.nc`, `.gcode`
    * Best for: Running pre-calculated paths from other CAM software.

> **[Visual Description - File Type Icons]**
> The image displays a row of file format icons commonly used in the software:
> * **SVG / DXF:** Represented by a pen tool or vector path icon.
> * **JPG / PNG:** Represented by an image or landscape icon.
> * **G-code:** Represented by a file sheet with a gear or "G" symbol.

---

## Importing & Design Issues

**Q: Why is my SVG file blank or missing lines after importing?**
* **Stroke Width:** Ensure your vector lines have a stroke width greater than 0. Hairline strokes may not be visible.
* **Color:** Avoid using white lines on a white background.
* **Text:** Live text fonts are not supported. You must "Convert to Outlines" or "Convert to Path" in your design software (e.g., Illustrator, Inkscape) before exporting.
* **Unsupported Features:** Complex features like clipping masks or gradients in SVGs may not import correctly. Simplify the design to basic paths.

> **[Visual Description - SVG Import Troubleshooting]**
> The image shows a comparison of two SVG files:
> * **Left (Incorrect):** A text object "HELLO" is selected, showing it is still a font object.
> * **Right (Correct):** The same "HELLO" text is shown with anchor points visible on the letters, indicating it has been converted to a vector path.

**Q: How do I improve the quality of my photo engraving?**
* **Contrast:** Use images with high contrast between the subject and the background.
* **Background:** Remove cluttered backgrounds. A solid white or transparent background works best.
* **Resolution:** Higher resolution images yield better detail in the generated relief.

**Q: Can I edit G-code after importing it?**
No. G-code files are "read-only" in the canvas. You can preview them in the **3D Preview** mode, but you cannot use ArtiMaker's editing tools (Scale, Rotate, Boolean) on imported G-code.

---

## Saving & Exporting

**Q: How do I save my project?**
You can save your current workspace as a project file (typically `.art` or `.json`) to retain all layers, parameters, and design elements for future editing.

**Q: How do I export for the machine?**
Once your design is ready:
1.  Click **Preview**.
2.  Click **Generate Toolpath**.
3.  Click **Download G-code** to save the `.gcode` file to your computer.

> **[Visual Description - Export Workflow]**
> The image highlights the "Download G-code" button in the 3D Preview interface:
> * The button is located in the **Machine Control** panel.
> * It becomes active (colored) only after the toolpath has been successfully generated.