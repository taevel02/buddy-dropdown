from setuptools import setup

import sys
import os
import glob

# Dynamically find mypyc generated modules (e.g., from charset_normalizer)
mypyc_modules = []
for p in sys.path:
    for f in glob.glob(os.path.join(p, "*__mypyc.*.so")):
        mypyc_modules.append(os.path.basename(f).split(".")[0])

APP = ["app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": [
        "PyQt6",
        "markitdown",
        "charset_normalizer",
        "requests",
        "certifi",
        "pdfplumber",
        "pdfminer",
        "markdown",
    ],
    "includes": mypyc_modules,
    "plist": {
        "CFBundleName": "Dropdown",
        "CFBundleDisplayName": "Dropdown",
        "CFBundleVersion": "1.0",
        "CFBundleShortVersionString": "1.0",
        "CFBundleIdentifier": "com.tae.buddy-dropdown",
        "CFBundleIconFile": "AppIcon.icns",
    },
    "iconfile": "AppIcon.icns",
}

setup(
    app=APP,
    name="Dropdown",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
