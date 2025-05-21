"""
Clean build script for the Arrival Skill Tool.
This script builds the application using a minimal spec file with only essential exclusions.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

# Configuration
SPEC_FILE = "clean_arrival_skill.spec"
UPX_DIR = r"C:\Users\Hello\Desktop\upx"  # Update this path if needed

def run_command(command, cwd=None):
    """Run a command and return its output"""
    print(f"Running: {command}")
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        cwd=cwd
    )
    if result.returncode != 0:
        print(f"Command failed with error code {result.returncode}")
        print(f"STDERR: {result.stderr}")
        return False, result.stdout
    return True, result.stdout

def clean_build_directories():
    """Clean up previous build directories"""
    print("\n=== Cleaning previous build directories ===")
    
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name} directory...")
            try:
                shutil.rmtree(dir_name)
                print(f"Successfully removed {dir_name}")
            except Exception as e:
                print(f"Error removing {dir_name}: {str(e)}")
                return False
    
    return True

def build_with_pyinstaller():
    """Build the executable with PyInstaller"""
    print("\n=== Building with PyInstaller ===")
    
    # Check if spec file exists
    if not os.path.exists(SPEC_FILE):
        print(f"Error: Spec file '{SPEC_FILE}' not found!")
        return False
    
    # Build command with UPX if available
    upx_option = f"--upx-dir=\"{UPX_DIR}\"" if os.path.exists(UPX_DIR) else ""
    
    # Build using the clean spec file with debug output
    start_time = time.time()
    success, output = run_command(f"pyinstaller {SPEC_FILE} {upx_option} --log-level=INFO")
    end_time = time.time()
    
    if not success:
        print("PyInstaller build failed")
        print(output)
        return False
    
    build_time = end_time - start_time
    print(f"PyInstaller build completed in {build_time:.2f} seconds")
    return True

def analyze_build_size():
    """Analyze the size of the build"""
    print("\n=== Analyzing build size ===")
    
    dist_dir = Path("dist") / "arrival_skill"
    if not dist_dir.exists():
        print(f"Build directory not found: {dist_dir}")
        return False
    
    # Get total size
    total_size = sum(f.stat().st_size for f in dist_dir.glob('**/*') if f.is_file())
    print(f"Total build size: {total_size / (1024*1024):.2f} MB")
    
    # List largest directories
    print("\nLargest directories:")
    dir_sizes = {}
    for file in dist_dir.glob('**/*'):
        if file.is_file():
            # Get the top-level directory
            rel_path = file.relative_to(dist_dir)
            top_dir = str(rel_path).split(os.sep)[0]
            if top_dir not in dir_sizes:
                dir_sizes[top_dir] = 0
            dir_sizes[top_dir] += file.stat().st_size
    
    # Sort and print directory sizes
    for dir_name, size in sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{dir_name}: {size / (1024*1024):.2f} MB")
    
    # List largest individual files
    print("\nLargest individual files:")
    files = [(f, f.stat().st_size) for f in dist_dir.glob('**/*') if f.is_file()]
    files.sort(key=lambda x: x[1], reverse=True)
    
    for file, size in files[:10]:
        print(f"{file.relative_to(dist_dir)}: {size / (1024*1024):.2f} MB")
    
    return True

def test_executable():
    """Test if the executable runs"""
    print("\n=== Testing executable ===")
    
    exe_path = Path("dist") / "arrival_skill" / "arrival_skill.exe"
    if not exe_path.exists():
        print(f"Error: Executable not found at {exe_path}")
        return False
    
    print("Attempting to run the executable...")
    print("This will open the application. Close it manually after testing.")
    
    # Run the executable with a timeout
    try:
        success, _ = run_command(f"start {exe_path}")
        if not success:
            print("Failed to start the executable")
            return False
        
        print("Executable started successfully")
        return True
    except Exception as e:
        print(f"Error running executable: {str(e)}")
        return False

def main():
    """Main build process"""
    print("=== Starting Clean Build Process for Arrival Skill Tool ===")
    
    steps = [
        ("Cleaning previous build directories", clean_build_directories),
        ("Building with PyInstaller", build_with_pyinstaller),
        ("Analyzing build size", analyze_build_size),
        ("Testing executable", test_executable)
    ]
    
    for step_name, step_func in steps:
        print(f"\n>>> {step_name}...")
        if not step_func():
            print(f"Step failed: {step_name}")
            return 1
    
    print("\n=== Build process completed successfully ===")
    print("The executable is located in the 'dist/arrival_skill' directory")
    return 0

if __name__ == "__main__":
    sys.exit(main())
