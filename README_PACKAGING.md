# Packaging Instructions for Arrival Skill Tool

This document explains how to create a lightweight executable package of the Arrival Skill Tool using PyInstaller with optimizations.

## Prerequisites

1. Make sure you have PyInstaller and UPX installed:
   ```
   pip install pyinstaller
   ```

2. Download UPX from https://github.com/upx/upx/releases and extract it to a folder on your system.
   Add the UPX folder to your PATH environment variable or note its location for later use.

## Building the Optimized Package

1. Use the optimized spec file to build the package:

   ```
   pyinstaller optimized_arrival_skill.spec
   ```

   If UPX is not in your PATH, specify its location:

   ```
   pyinstaller --upx-dir="C:\path\to\upx" optimized_arrival_skill.spec
   ```

2. The optimized executable will be created in the `dist\arrival_skill` folder.

## Optimization Details

The optimized spec file includes several techniques to reduce the final executable size:

1. **Selective Module Inclusion**: Only necessary modules are included, drastically reducing size.

2. **Language Model Filtering**: Only English language models for PaddleOCR are included.

3. **Exclusion of Unnecessary Components**: Many unused parts of large libraries like Paddle, NumPy, and others are excluded.

4. **UPX Compression**: The executable is compressed using UPX for further size reduction.

5. **Windowed Mode**: The application runs in windowed mode without a console.

## Troubleshooting

If the executable fails to run:

1. Try running it from the command line to see any error messages.

2. If specific modules are missing, you may need to add them to the `hidden_imports` list in the spec file.

3. If model files are not found, check the paths in the `datas` section of the spec file and adjust them according to your Python installation path.

## Further Size Optimization

If you need to reduce the size even more:

1. Consider using a custom-trained lightweight OCR model specifically for your use case.

2. Use the `--onefile` option with PyInstaller, but be aware that startup time will increase.

3. Manually delete unnecessary model files from the PaddleOCR installation before packaging.

4. Use a tool like "Dependency Walker" to identify and remove unused DLLs from the final package.