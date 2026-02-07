'''
INIT.PY
Usage: python3 init.py "ProjectName"
Function: Creates folder structure and initial manifest.
'''

import sys
import os
import json
import datetime
from pathlib import Path

# --- CONFIGURATION ---
# Resolve 'projects' dir relative to this script (../projects)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_ROOT = SCRIPT_DIR.parent / "projects"

LAYERS = ['raw', 'processed', 'export']
TYPES = ['video', 'audio']

def main():
    # 1. Input Validation
    if len(sys.argv) < 2:
        print("❌ Error: Missing project name.")
        print("Usage: python3 init.py \"ProjectName\"")
        sys.exit(1)

    name_input = sys.argv[1]
    
    # 2. Name Sanitization (Only allow alphanumeric, hyphens, underscores)
    safe_suffix = "".join([c for c in name_input if c.isalnum() or c in (' ', '-', '_')]).strip()
    today = datetime.date.today().strftime("%Y-%m-%d")
    folder_name = f"{today}_{safe_suffix}"
    
    project_path = PROJECTS_ROOT / folder_name

    # 3. Create Project
    if project_path.exists():
        print(f"⚠️  Project '{folder_name}' already exists.")
        # We don't exit here, we might just be re-initializing a broken folder
    else:
        print(f"Creating project: {folder_name}")

    try:
        # Create ../projects if it doesn't exist
        if not PROJECTS_ROOT.exists():
            PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

        # Create Subfolders
        for layer in LAYERS:
            for type_ in TYPES:
                path = project_path / layer / type_
                path.mkdir(parents=True, exist_ok=True)

        # 4. Create Initial Manifest
        manifest_path = project_path / "manifest.json"
        if not manifest_path.exists():
            manifest = {
                "project": folder_name,
                "created": datetime.datetime.now().isoformat(),
                "state": "INIT",
                "files": {layer: {"video": [], "audio": []} for layer in LAYERS}
            }
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            print("✓ Manifest created.")
        
        print(f"✓ Project structure ready.")
        print(f"📂 Location: {project_path}")

    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
