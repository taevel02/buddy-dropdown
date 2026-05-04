# BUDDY DROPDOWN

Dropdown is a macOS application that provides a clean interface for bidirectional document conversion:

- **PDF to Markdown**: Converts `.pdf` files to `.md` using `markitdown`.
- **Markdown to PDF**: Converts `.md` files to `.pdf` using the `markdown` library and PyQt6.

This guide details how to install dependencies, run the application locally, and package it into a macOS `.app` bundle using `py2app`.

## Prerequisites

Make sure you have Python 3 installed on your macOS system. It is highly recommended to use a virtual environment.

## 1. Setup Environment and Install Dependencies

Open your terminal, navigate to the `buddy-dropdown` directory, and run the following commands:

```bash
# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

## 2. Run the App Locally (Testing)

Before packaging the app, you can test it directly using Python:

```bash
python3 app.py
```

A window will open with a toggle button at the top to choose between **`.pdf ➔ .md`** and **`.md ➔ .pdf`** modes. Depending on the selected mode, you can drag and drop multiple `.pdf` or `.md` files into the Drop Zone. The converted files will be saved in the same directory as the original files.

## 3. Build the macOS .app Bundle

Once you confirm the app works locally, you can build the standalone `.app` bundle using `py2app`.

```bash
# Run the setup script to build the app
python3 setup.py py2app
```

This process might take a few minutes as it bundles all dependencies (PyQt6, markitdown, etc.) into the app.

### Development vs Production Build

If you want to build an alias bundle for testing without fully copying all dependencies (faster), you can run:

```bash
python3 setup.py py2app -A
```

## 4. Run the Packaged App

After the build process completes, you will find a new `dist` folder in your directory.

You can run your app by either:

- Double-clicking `Dropdown.app` inside the `dist` folder via Finder.
- Or running it from the terminal:

```bash
open dist/Dropdown.app
```

## 5. Automated GitHub Releases (.dmg)

This project is configured with GitHub Actions to automatically build and release a `.dmg` installer.

1. Commit your changes and push them to the `main` branch:
   ```bash
   git push origin main
   ```
2. Create a version tag (must start with `v`, e.g., `v1.0.0`) and push it:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions will automatically:
   - Build the macOS `.app` using `py2app`.
   - Package it into a `.dmg` file using `create-dmg`.
   - Create a new GitHub Release and upload the `.dmg` file.

You can then download the installer directly from the repository's **Releases** page!
