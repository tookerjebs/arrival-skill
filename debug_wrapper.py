"""
Debug wrapper for the main application.
This script will catch any exceptions, log them to a file, and keep the window open.
"""

import sys
import os
import traceback
import time
import importlib

# Create a log file in the same directory as the executable
log_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "error_log.txt")

def log_message(message):
    """Log a message to both console and file"""
    print(message)
    with open(log_file, "a") as f:
        f.write(message + "\n")

def main():
    """Main function that runs the application and catches exceptions"""
    log_message(f"Starting application at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"Python version: {sys.version}")
    log_message(f"Executable path: {sys.executable}")

    # Log sys.path
    log_message("\nPython path:")
    for path in sys.path:
        log_message(f"  {path}")

    # Log available PIL modules
    try:
        import PIL
        log_message(f"\nPIL version: {PIL.__version__}")
        log_message("Available PIL modules:")
        for module in dir(PIL):
            log_message(f"  PIL.{module}")
    except Exception as e:
        log_message(f"Error importing PIL: {str(e)}")

    try:
        # Try to import the main module
        log_message("\nAttempting to import main module...")
        import main

        # Run the main application
        log_message("Running main application...")
        app = main.SkillRerollApp()
        app.run()

        log_message("Application completed successfully")
    except ImportError as e:
        log_message(f"Import Error: {str(e)}")
        log_message("\nDetailed traceback:")
        log_message(traceback.format_exc())

        # Try to diagnose the specific ImageDraw import error
        if "ImageDraw" in str(e):
            log_message("\nDiagnosing PIL.ImageDraw import error:")
            try:
                from PIL import Image
                log_message("Successfully imported PIL.Image")
            except Exception as img_err:
                log_message(f"Error importing PIL.Image: {str(img_err)}")

            # Check if ImageDraw.py exists in the bundle
            if hasattr(sys, '_MEIPASS'):
                pil_dir = os.path.join(sys._MEIPASS, 'PIL')
                if os.path.isdir(pil_dir):
                    log_message(f"PIL directory exists at: {pil_dir}")
                    log_message("Files in PIL directory:")
                    for file in os.listdir(pil_dir):
                        log_message(f"  {file}")
                else:
                    log_message(f"PIL directory not found at: {pil_dir}")
    except Exception as e:
        log_message(f"Unhandled Exception: {str(e)}")
        log_message("\nDetailed traceback:")
        log_message(traceback.format_exc())

    # Keep the window open
    log_message("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
