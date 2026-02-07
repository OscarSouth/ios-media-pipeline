'''
STATUS.PY
Usage: python3 status.py "ProjectName"
Function: Prints a detailed dashboard for a specific project.
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
        print("Usage: python3 status.py \"ProjectName\"")
        sys.exit(1)

    name_input = sys.argv[1]
    project_path = get_project_path(name_input)
    
    if not project_path:
        print(f"❌ Project containing '{name_input}' not found.")
        sys.exit(1)

    manifest_path = project_path / "manifest.json"
    if not manifest_path.exists():
        print(f"❌ Manifest not found in {project_path.name}")
        print("Run 'update.py' to generate it.")
        sys.exit(1)

    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ JSON Error: {e}")
        sys.exit(1)

    # --- REPORT GENERATION ---
    state = data.get('state', 'UNKNOWN')
    project_name = data.get('project', project_path.name)
    created = data.get('created', '').split('T')[0] # Just the date part
    files = data.get('files', {})

    print("\n" + "="*40)
    print(f" 🎬 PROJECT DASHBOARD")
    print("="*40)
    print(f" Name:    {project_name}")
    print(f" Created: {created}")
    print(f" State:   [{state}]")
    print("-" * 40)

    total_project_duration = 0.0

    for layer in LAYERS:
        print(f" {layer.upper()}")
        layer_files_found = False
        
        for type_ in TYPES:
            file_list = files.get(layer, {}).get(type_, [])
            count = len(file_list)
            
            if count > 0:
                layer_files_found = True
                
                # Sum duration
                type_dur = sum(f.get('meta', {}).get('duration', 0) for f in file_list)
                total_project_duration += type_dur
                
                # Convert to mm:ss
                m = int(type_dur // 60)
                s = int(type_dur % 60)
                
                print(f"   • {type_.capitalize()}: {count} files ({m}m {s}s)")
                
                # Preview 2 files
                for item in file_list[:2]:
                    res = item.get('meta', {}).get('resolution', '-')
                    print(f"       - {item['name']} [{res}]")
                if count > 2:
                    print(f"       ... (+{count-2} more)")
        
        if not layer_files_found:
            print("   (Empty)")
        print("-" * 40)

    # Total Footer
    tm = int(total_project_duration // 60)
    ts = int(total_project_duration % 60)
    print(f" ⏱ TOTAL FOOTAGE: {tm}m {ts}s")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    main()
