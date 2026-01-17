---
description: Build the DZSynapse application as a standalone .exe
---

This workflow will package your Python application into a single executable file using PyInstaller.

1.  **Install PyInstaller**
    We need `pyinstaller` to create the executable.
    ```powershell
    pip install pyinstaller
    ```

2.  **Clean Previous Builds**
    Remove old build folders to ensure a clean slate.
    ```powershell
    Remove-Item -Path dist, build, *.spec -Recurse -ErrorAction SilentlyContinue
    ```

3.  **Build the Executable**
    We run PyInstaller with specific flags:
    *   `--onefile`: Create a single .exe file.
    *   `--noconsole`: Hide the terminal window (GUI only).
    *   `--hidden-import`: Explicitly include `tkcalendar`, `babel.numbers`, and `PIL` dependencies.
    *   `--add-data`: Bundle the `logo.png` inside the exe.
    *   `--icon`: Use `logo.png` as the application icon.
    // turbo
    ```powershell
    pyinstaller --noconsole --onefile --hidden-import=tkcalendar --hidden-import=babel.numbers --hidden-import=PIL --add-data "logo.png;." --icon="logo.png" --name "DZSynapse_Setup" main.py
    ```

4.  **Prepare Distribution Folder**
    We need to make sure the external data (Wilaya folder) is next to the exe, as we programmed it to look in the current directory.
    ```powershell
    New-Item -ItemType Directory -Force -Path "dist/DZSynapse_Dist"
    Move-Item -Path "dist/DZSynapse_Setup.exe" -Destination "dist/DZSynapse_Dist/"
    Copy-Item -Path "Wilaya-Of-Algeria" -Destination "dist/DZSynapse_Dist/Wilaya-Of-Algeria" -Recurse
    Copy-Item -Path "logo.png" -Destination "dist/DZSynapse_Dist/"
    ```

5.  **Finish**
    Your portable application is ready in `dist/DZSynapse_Dist`.
    You can Zip this folder and send it to any Windows PC!
