import os
import sys
import platform
import shutil
import stat
import subprocess
from pathlib import Path

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def print_step(msg):
    print(f"\n{'-'*50}\n{msg}\n{'-'*50}")

def get_sublime_packages_dir():
    """Locates the Sublime Text Packages directory based on the OS."""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return None
        paths = [
            Path(appdata) / "Sublime Text" / "Packages",
            Path(appdata) / "Sublime Text 3" / "Packages"
        ]
    elif system == "Darwin":
        paths = [
            home / "Library" / "Application Support" / "Sublime Text" / "Packages",
            home / "Library" / "Application Support" / "Sublime Text 3" / "Packages"
        ]
    else: # Linux
        paths = [
            home / ".config" / "sublime-text" / "Packages",
            home / ".config" / "sublime-text-3" / "Packages"
        ]
        
    for p in paths:
        if p.exists() and p.is_dir():
            return p
    return None

def main():
    print("Starting dev deployment of the Incomprehensible-ex plugin...")

    print_step("1. Locating Sublime Text Packages Folder")
    packages_dir = get_sublime_packages_dir()
    
    if packages_dir:
        print(f"Found Packages directory: {packages_dir}")
    else:
        print("Could not find Sublime Text Packages directory automatically.")
        user_input = input("Please enter the full path to your Packages folder: ").strip()
        packages_dir = Path(user_input)
        if not packages_dir.exists() or not packages_dir.is_dir():
            print("Invalid directory. Exiting.")
            sys.exit(1)

    print_step("2. Preparing target directory")
    plugin_name = "Incomprehensible Ex"
    target_dir = packages_dir / plugin_name
    src_dir = Path(__file__).resolve().parent.parent

    print(f"Source: {src_dir}")
    print(f"Target: {target_dir}")

    if target_dir.exists() or target_dir.is_symlink():
        print(f"Removing existing installation at {target_dir}...")
        try:
            if target_dir.is_symlink():
                target_dir.unlink()
            elif platform.system() == "Windows":
                # Try removing as a junction first (rmdir handles junctions without deleting contents)
                res = subprocess.run(["cmd", "/c", "rmdir", str(target_dir)], capture_output=True)
                if res.returncode != 0:
                    # If it wasn't a junction or wasn't empty, use rmtree
                    shutil.rmtree(target_dir, onerror=remove_readonly)
            else:
                shutil.rmtree(target_dir, onerror=remove_readonly)
        except Exception as e:
            print(f"Error removing existing directory: {e}")
            sys.exit(1)

    print_step("3. Creating live symlink/junction")
    try:
        system = platform.system()
        if system == "Windows":
            # Create a directory junction (doesn't require admin rights like symlinks do on Windows)
            subprocess.run(["cmd", "/c", "mklink", "/J", str(target_dir), str(src_dir)], check=True)
            print("Directory junction created successfully.")
        else:
            os.symlink(src_dir, target_dir)
            print("Symlink created successfully.")
    except Exception as e:
        print(f"Error creating symlink/junction: {e}")
        print("\nFallback: You may need to run this script as Administrator.")
        sys.exit(1)

    print_step("4. Deployment Complete!")
    print(f"The plugin is now linked to:\n  {target_dir}")
    print("\nBecause it is linked, changes to your source files will be instantly loaded by Sublime Text!")
    print("You DO NOT need to restart Sublime Text or re-run this script when editing files.")

if __name__ == "__main__":
    main()
