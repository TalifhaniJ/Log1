# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 11:04:31 2024

@author: Talifhani Khomola
"""

import os
import PyInstaller.__main__


# Define the main application file and the icon file
main_app_file = 'app.py'
#icon_file = 'C:/Users/Talifhani Khomola/Documents/v1/app/icon.png'  # Update this path to your icon file

# Clean previous builds
# if os.path.exists('build'):
#     os.rmdir('build')
# if os.path.exists('dist'):
#     os.rmdir('dist')
# if os.path.exists('wisapp.spec'):
#     os.remove('wisapp.spec')

# Create the executable with the specified icon
PyInstaller.__main__.run([
    '--name=WISLogging',
    '--hidden-import=win32timezone',
    '--icon=icon.ico',
    '--add-data=icon.ico:.',
    '--onefile',
    '--console',  # Ensure the app runs in the console
    main_app_file
])