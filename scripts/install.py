import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_step(msg):
    print(f"\n{'-'*50}\n{msg}\n{'-'*50}")

def get_sublime_packages_dir():
    """Locates the Sublime Text Packages directory based on the OS."""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
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

def run_command(cmd, **kwargs):
    """Executes a shell command and handles basic errors."""
    print(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {cmd}")
        return False
    return True

def main():
    print("Starting manual installation of the Incomprehensible-ex fork...")

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

    print_step("2. Cloning the repository")
    target_dir = packages_dir / "Incomprehensible Ex"
    if target_dir.exists():
        print(f"Target directory already exists: {target_dir}")
        print("Skipping clone. (You may want to update it manually via 'git pull')")
    else:
        clone_cmd = 'git clone -b develop https://github.com/yuxiaoli/Incomprehensible-ex.git "Incomprehensible Ex"'
        success = run_command(clone_cmd, cwd=packages_dir)
        if not success:
            print("Failed to clone repository. Exiting.")
            sys.exit(1)

    print_step("3. Installing required system tools")
    system = platform.system()
    python_cmd = None
    if system == "Windows":
        python_cmd = "py"
        run_command("winget install JohnMacFarlane.Pandoc")
        run_command('py -m pip install docling "markitdown[all]"')
    elif system == "Darwin":
        python_cmd = "python3"
        run_command("brew install pandoc antiword")
        run_command('python3 -m pip install --user docling "markitdown[all]"')
    elif system == "Linux":
        python_cmd = "python3"
        run_command("sudo apt update")
        run_command("sudo apt install -y pandoc antiword poppler-utils python3-pip")
        run_command('python3 -m pip install --user docling "markitdown[all]"')
    else:
        print(f"Unsupported operating system: {system}. Please install pandoc, docling, and markitdown manually.")

    print_step("4. Verifying commands")
    pandoc_ok = shutil.which("pandoc") is not None
    docling_ok = False
    markitdown_ok = False

    if pandoc_ok:
        run_command("pandoc --version")
    else:
        print("Warning: 'pandoc' command not found in PATH.")

    if python_cmd:
        docling_ok = run_command(
            f'{python_cmd} -c "import docling; print(\'docling ok\')"'
        )
        markitdown_ok = run_command(
            f'{python_cmd} -c "import markitdown; print(\'markitdown ok\')"'
        )

    if not docling_ok:
        print("Warning: 'docling' Python package is not available in the selected system Python.")

    if not markitdown_ok:
        print("Warning: 'markitdown' Python package is not available in the selected system Python.")

    if not (pandoc_ok and docling_ok and markitdown_ok):
        print("\nNote: If Sublime cannot find them, restart Sublime from a terminal so it")
        print("inherits your PATH, or add the tool locations to your system PATH.")

    print_step("5. Installation Complete!")
    print("Please restart Sublime Text to load the new plugin.")
    print("\nTo change settings in Sublime Text:")
    print("Ctrl/Cmd+Shift+P -> Incomprehensible Ex: Manage Settings")

if __name__ == "__main__":
    main()
