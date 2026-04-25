from setuptools import setup

APP = ["app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["PyQt6", "markitdown"],
    "includes": [],
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
