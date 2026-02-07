'''
ARCHIVE.PY
Usage: python3 archive.py "ProjectName"
Function: Locks state, generates readable README, prepares for move.
'''

import sys
import os
import json
from pathlib import Path

# --- CONFIGURATION ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_ROOT = SCRIPT_DIR.parent / "projects"
LAYERS = ['raw', 'processed', 'export']
TYPES = ['video', 'audio']

def get_project_path(name_fragment):
    if not PROJECTS_ROOT.exists(): return None
    for path in PROJECTS_ROOT.iterdir():
        if path.is_dir() and path.name.lower().endswith(f"_{name_fragment.lower()}"):
            return path
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 archive.py \"ProjectName\"")
        sys.exit(1)

    name_input = sys.argv[1]
    project_path = get_project_path(name_input)
    
    if not project_path:
        print(f"❌ Project containing '{name_input}' not found.")
        sys.exit(1)

    manifest_path = project_path / "manifest.json"
    if not manifest_path.exists():
        print("❌ Manifest not found. Run 'update.py' first.")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # 1. Validation: Check for exports
    exports = manifest['files']['export']['video'] + manifest['files']['export']['audio']
    if not exports:
        print("⚠️  WARNING: No files found in 'export' folder.")
        confirm = input("Are you sure you want to archive? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # 2. Update State
    manifest['state'] = "ARCHIVED"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # 3. Generate README_ARCHIVE.txt
    readme_path = project_path / "README_ARCHIVE.txt"
    try:
        with open(readme_path, 'w') as f:
            f.write(f"PROJECT ARCHIVE RECORD\n")
            f.write(f"Project:  {manifest['project']}\n")
            f.write(f"Created:  {manifest.get('created', 'N/A')}\n")
            f.write(f"Status:   ARCHIVED\n")
            f.write("="*50 + "\n\n")
            
            for layer in LAYERS:
                f.write(f"[{layer.upper()}]\n")
                has_files = False
                for type_ in TYPES:
                    files = manifest['files'][layer][type_]
                    if files:
                        has_files = True
                        f.write(f"  {type_.upper()} ({len(files)} files):\n")
                        for item in files:
                            meta = item.get('meta', {})
                            dur = meta.get('duration', 0)
                            res = meta.get('resolution', 'N/A')
                            # Format line:  - Filename (12.5s, 3840x2160)
                            f.write(f"    - {item['name']} ({dur:.1f}s, {res})\n")
                
                if not has_files:
                    f.write("  (Empty)\n")
                f.write("\n")
                
        print(f"✓ Project locked to ARCHIVED.")
        print(f"✓ Generated: {readme_path.name}")
        print(f"📂 READY. You may now move '{project_path.name}' to cold storage.")

    except Exception as e:
        print(f"❌ Error writing README: {e}")

if __name__ == "__main__":
    main()
