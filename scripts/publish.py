import os
import sys
import subprocess
import re
from pathlib import Path

def print_header(msg):
    print(f"\n{'-'*50}\n{msg}\n{'-'*50}")

def run_cmd(cmd, env=None, check=True, capture=False):
    """Run a shell command and return its output or success status."""
    try:
        res = subprocess.run(cmd, shell=True, check=check, capture_output=capture, text=True, env=env)
        if capture:
            return res.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        if capture:
            return ""
        print(f"Command failed with exit code {e.returncode}: {cmd}")
        if e.stdout:
            print(e.stdout.strip())
        if e.stderr:
            print(e.stderr.strip())
        return False

def load_env_token(root_dir):
    """Load GH_TOKEN from the .env file in the root directory."""
    env_path = root_dir / ".env"
    token = None
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "GH_TOKEN":
                        token = v.strip()
                        break
    return token

def check_forbidden_files():
    """Ensure generated/local files are not tracked by Git."""
    tracked = run_cmd("git ls-files", capture=True)
    if not tracked:
        return True
        
    forbidden = []
    for f in tracked.split('\n'):
        if f.endswith('.pyc') or '__pycache__' in f or f == 'package-metadata.json':
            forbidden.append(f)
            
    if forbidden:
        print("Error: The following forbidden files are tracked in Git:")
        for f in forbidden:
            print(f"  - {f}")
        print("\nPlease remove them before publishing using:")
        print("  git rm --cached <file>")
        return False
    return True

def check_required_files(root_dir):
    """Ensure README and LICENSE exist."""
    missing = []
    if not (root_dir / "README.md").exists():
        missing.append("README.md")
    
    # Check for any common license file name
    license_exists = any((root_dir / name).exists() for name in ["LICENSE", "LICENSE.md", "LICENSE.txt"])
    if not license_exists:
        missing.append("LICENSE")
        
    if missing:
        print("Warning: The following recommended files are missing:")
        for m in missing:
            print(f"  - {m}")
        ans = input("Continue anyway? (y/n): ").strip().lower()
        if ans != 'y':
            return False
    return True

def main():
    root_dir = Path(__file__).resolve().parent.parent
    os.chdir(root_dir)

    print_header("Sublime Text Plugin Publisher")

    # 1. Check tools
    if not run_cmd("git --version", capture=True):
        print("Error: Git is required but not found in PATH.")
        sys.exit(1)
    if not run_cmd("gh --version", capture=True):
        print("Error: GitHub CLI (gh) is required but not found in PATH.")
        sys.exit(1)

    # 2. Check Repository State
    print("Checking repository state...")
    if not check_forbidden_files():
        sys.exit(1)
    if not check_required_files(root_dir):
        sys.exit(1)

    # 3. Handle uncommitted changes
    status = run_cmd("git status --porcelain", capture=True)
    if status:
        print("\nYou have uncommitted changes:")
        print(status)
        ans = input("\nDo you want to commit these changes before releasing? (y/n): ").strip().lower()
        if ans == 'y':
            msg = input("Commit message: ").strip() or "Prepare release"
            run_cmd("git add .")
            run_cmd(f'git commit -m "{msg}"')
        else:
            print("Please commit or stash your changes before publishing.")
            sys.exit(1)

    # 4. Version Tagging
    print_header("Version Tagging")
    print("Package Control expects semantic version tags (e.g., 1.0.0, 1.0.1).")
    version = input("Enter new release tag: ").strip()
    
    if not re.match(r"^v?\d+\.\d+\.\d+", version):
        print("Warning: The version doesn't look like standard SemVer (e.g., 1.0.0).")
        ans = input("Continue with this tag? (y/n): ").strip().lower()
        if ans != 'y':
            sys.exit(1)

    # 5. Git Tag and Push
    print_header(f"Publishing Release: {version}")
    
    print("Tagging release...")
    if not run_cmd(f'git tag {version}', check=False):
        print("Failed to create tag. Does it already exist?")
        sys.exit(1)

    print("Pushing commits to origin...")
    run_cmd("git push origin HEAD")
    
    print(f"Pushing tag {version} to origin...")
    run_cmd(f"git push origin {version}")

    # 6. GitHub Release via gh CLI
    print_header("Creating GitHub Release")
    token = load_env_token(root_dir)
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
        print("Loaded GH_TOKEN from .env")
    else:
        print("Warning: GH_TOKEN not found in .env. Using global gh auth state if available.")

    release_cmd = f'gh release create {version} --generate-notes -t "Release {version}"'
    success = run_cmd(release_cmd, env=env, check=False)

    if success:
        print_header("Publish Complete!")
        print(f"Successfully released version {version} to GitHub.")
        print("\nNext steps for Package Control:")
        print("1. Fork https://github.com/wbond/package_control_channel")
        print("2. Add your package JSON entry in the appropriate repository file")
        print("3. Open a Pull Request on Package Control Channel")
    else:
        print("\nFailed to create GitHub release via CLI.")
        print("You may need to create the release manually on GitHub.")

if __name__ == "__main__":
    main()
