# -*- coding: utf-8 -*-
"""
Setup script for creating MTN Recommendation System executable
"""

import os
import sys
import shutil
from PIL import Image
import PyInstaller.__main__

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(current_dir, "Recommendation_Engine_Version_5.py")
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

# Define PyInstaller arguments
pyinstaller_args = [
    main_script,
    '--name=MTN_Recommendation_System',
    '--onefile',
    '--windowed',
    '--clean',
    f'--workpath={os.path.join(current_dir, "build")}',
    f'--distpath={os.path.join(current_dir, "dist")}',
    f'--specpath={current_dir}',
    '--add-data={}:{}'.format(logo_file.replace('\\', '/'), '.'),
    '--add-data={}:{}'.format(subscriber_file.replace('\\', '/'), '.'),
    '--add-data={}:{}'.format(product_file.replace('\\', '/'), '.'),
    '--add-data={}:{}'.format(credentials_file.replace('\\', '/'), '.'),
    # Add hidden imports for libraries that might not be automatically detected
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=pandas',
    '--hidden-import=vertexai',
    '--hidden-import=google.cloud.aiplatform',
]

# Add icon if available
if icon_file and os.path.exists(icon_file):
    pyinstaller_args.append(f'--icon={icon_file}')

# Run PyInstaller
print("\n" + "="*60)
print("BUILDING MTN RECOMMENDATION SYSTEM EXECUTABLE")
print("="*60)
print("\nStarting PyInstaller with arguments:")
for arg in pyinstaller_args:
    print(f"  {arg}")

PyInstaller.__main__.run(pyinstaller_args)

# Create a resources folder in the dist directory
dist_dir = os.path.join(current_dir, "dist")
resources_dir = os.path.join(dist_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

# Copy additional resources to the dist folder
print("\nCopying additional resources to distribution folder...")
for resource in [logo_file, subscriber_file, product_file, credentials_file]:
    if os.path.exists(resource):
        shutil.copy2(resource, resources_dir)
        print(f"  Copied {os.path.basename(resource)} to resources folder")

print("\n" + "="*60)
print("BUILD COMPLETED SUCCESSFULLY!")
print("="*60)
print(f"\nExecutable created at: {os.path.join(dist_dir, 'MTN_Recommendation_System.exe')}")
print(f"Resources copied to: {resources_dir}")
print("\nYou can now distribute the executable and resources folder together.")