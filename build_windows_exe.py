# -*- coding: utf-8 -*-
"""
Build script for creating a standalone Windows executable for MTN Recommendation System
"""

import os
import sys
import shutil
from PIL import Image
import PyInstaller.__main__

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(current_dir, "MTN_Recommendation_System_Web.py")
logo_file = os.path.join(current_dir, "New-mtn-logo.jpg")
icon_file = os.path.join(current_dir, "mtn_icon.ico")
subscriber_file = os.path.join(current_dir, "SubscriberProfileData.csv")
product_file = os.path.join(current_dir, "ProductCatalogue.csv")
credentials_file = os.path.join(current_dir, "hackathon2025-454908-0a52f19ef9b1.json")

# Create icon file if it doesn't exist
if not os.path.exists(icon_file) and os.path.exists(logo_file):
    try:
        img = Image.open(logo_file)
        # Create multiple sizes for better icon quality
        img.save(icon_file, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"Created icon file: {icon_file}")
    except Exception as e:
        print(f"Could not create icon file: {e}")
        icon_file = None

# Ensure all required files exist
required_files = [
    (main_script, "Main Python script"),
    (logo_file, "MTN Logo"),
    (subscriber_file, "Subscriber data"),
    (product_file, "Product catalogue"),
    (credentials_file, "Google API credentials")
]

missing_files = []
for file_path, description in required_files:
    if not os.path.exists(file_path):
        missing_files.append(f"{description} ({file_path})")

if missing_files:
    print("ERROR: The following required files are missing:")
    for missing in missing_files:
        print(f"  - {missing}")
    print("\nPlease ensure all required files are present before building the executable.")
    sys.exit(1)

# Create a launcher script that will be the actual entry point
launcher_script = os.path.join(current_dir, "streamlit_launcher.py")
with open(launcher_script, "w") as f:
    f.write("""
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import threading
import webbrowser
import time
import socket
import tempfile
import shutil
import atexit

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]

def open_browser(port):
    # Wait a moment for the server to start
    time.sleep(3)
    webbrowser.open(f'http://localhost:{port}')

def extract_resources(temp_dir):
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
        exe_dir = app_dir
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
        exe_dir = app_dir
    
    # Copy required files to temp directory
    required_files = [
        "MTN_Recommendation_System_Web.py",
        "New-mtn-logo.jpg",
        "SubscriberProfileData.csv",
        "ProductCatalogue.csv",
        "hackathon2025-454908-0a52f19ef9b1.json"
    ]
    
    for file in required_files:
        source = os.path.join(exe_dir, file)
        if os.path.exists(source):
            shutil.copy2(source, temp_dir)
    
    return temp_dir

def cleanup_temp_dir(temp_dir):
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

def main():
    # Create a temporary directory for extracted files
    temp_dir = tempfile.mkdtemp(prefix="mtn_recommendation_")
    atexit.register(cleanup_temp_dir, temp_dir)
    
    # Extract resources to temp directory
    working_dir = extract_resources(temp_dir)
    
    # Change to the working directory
    os.chdir(working_dir)
    
    # Find a free port
    port = find_free_port()
    
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = str(port)
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Start browser in a separate thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    # Start Streamlit
    main_script = os.path.join(working_dir, "MTN_Recommendation_System_Web.py")
    
    try:
        # Run streamlit as a module
        streamlit_cmd = [sys.executable, "-m", "streamlit", "run", 
                         main_script, 
                         "--server.port", str(port),
                         "--server.headless", "true",
                         "--browser.gatherUsageStats", "false"]
        
        process = subprocess.Popen(streamlit_cmd)
        process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup will happen via atexit handler
        pass

if __name__ == "__main__":
    main()
""")

# Define PyInstaller arguments for a standalone executable
pyinstaller_args = [
    launcher_script,  # Use the launcher script as the entry point
    '--name=MTN_Recommendation_System',
    '--onefile',  # Create a single executable
    '--noconsole',  # No console window
    '--clean',
    f'--workpath={os.path.join(current_dir, "build")}',
    f'--distpath={os.path.join(current_dir, "dist")}',
    f'--specpath={current_dir}',
    # Add all required files as data
    f'--add-data={main_script};.',
    f'--add-data={logo_file};.',
    f'--add-data={subscriber_file};.',
    f'--add-data={product_file};.',
    f'--add-data={credentials_file};.',
    # Add hidden imports for libraries
    '--hidden-import=streamlit',
    '--hidden-import=pandas',
    '--hidden-import=matplotlib',
    '--hidden-import=PIL',
    '--hidden-import=vertexai',
    '--hidden-import=google.cloud.aiplatform',
    '--hidden-import=openpyxl',
    # Collect all packages
    '--collect-all=streamlit',
    '--collect-all=pandas',
    '--collect-all=matplotlib',
    '--collect-all=PIL',
    '--collect-all=vertexai',
    '--collect-all=google.cloud',
    '--collect-all=openpyxl',
]

# Add icon if available
if icon_file and os.path.exists(icon_file):
    pyinstaller_args.append(f'--icon={icon_file}')

# Run PyInstaller
print("\n" + "="*60)
print("BUILDING MTN RECOMMENDATION SYSTEM STANDALONE EXECUTABLE")
print("="*60)
print("\nStarting PyInstaller with arguments:")
for arg in pyinstaller_args:
    print(f"  {arg}")

PyInstaller.__main__.run(pyinstaller_args)

# Clean up the temporary launcher script
if os.path.exists(launcher_script):
    os.remove(launcher_script)

print("\n" + "="*60)
print("BUILD COMPLETED SUCCESSFULLY!")
print("="*60)
print(f"\nStandalone executable created at: {os.path.join(current_dir, 'dist', 'MTN_Recommendation_System.exe')}")
print("\nThis is a completely standalone executable that includes all dependencies.")
print("Just double-click the .exe file to run the application.")