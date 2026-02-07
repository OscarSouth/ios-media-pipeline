'''
UPDATE.PY
Usage: python3 update.py "ProjectName"
Function: Scans all layers, renames new files (sorted by date), extracts metadata, updates state.
'''

import sys
import os
import json
import subprocess
from pathlib import Path

# --- CONFIGURATION ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_ROOT = SCRIPT_DIR.parent / "projects"

VIDEO_EXTS = {'.mov', '.mp4', '.m4v'}
AUDIO_EXTS = {'.wav', '.mp3', '.m4a', '.aac', '.aiff'}
LAYERS = ['raw', 'processed', 'export']
TYPES = ['video', 'audio']

# --- HELPER FUNCTIONS ---

def get_project_path(name_fragment):
    """Finds path for YYYY-MM-DD_NameFragment."""
    if not PROJECTS_ROOT.exists():
        return None
    # Case-insensitive search for the name fragment at end of folder name
    for path in PROJECTS_ROOT.iterdir():
        if path.is_dir() and path.name.lower().endswith(f"_{name_fragment.lower()}"):
            return path
    return None

def get_file_metadata(filepath):
    """Uses ffprobe to extract Duration and Creation Date."""
    # a-Shell requires standard ffmpeg command structure
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_format', '-show_streams', str(filepath)
    ]
    meta = {"duration": 0.0, "created": "", "resolution": "N/A"}
    
    try:
        # Run process
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        # 1. Duration
        if 'format' in data and 'duration' in data['format']:
            meta['duration'] = float(data['format']['duration'])
            
        # 2. Creation Time (Best effort for sorting)
        tags = data.get('format', {}).get('tags', {})
        meta['created'] = tags.get('creation_time', "")
        
        # 3. Resolution (First video stream)
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                w = stream.get('width')
                h = stream.get('height')
                if w and h:
                    meta['resolution'] = f"{w}x{h}"
                    break
    except Exception:
        # If ffprobe fails or file is corrupt, use OS stats
        try:
            meta['created'] = str(os.path.getmtime(filepath))
        except:
            pass
            
    return meta

def process_layer(project_path, project_name, date_str, layer):
    """Renames and inventories files for a specific layer."""
    layer_path = project_path / layer
    inventory = {"video": [], "audio": []}
    
    for type_ in TYPES:
        type_path = layer_path / type_
        if not type_path.exists():
            continue
            
        # --- A. Gather Files (Recursive) ---
        all_files = []
        valid_exts = VIDEO_EXTS if type_ == 'video' else AUDIO_EXTS
        
        for root, _, files in os.walk(type_path):
            for f in files:
                if Path(f).suffix.lower() in valid_exts:
                    all_files.append(Path(root) / f)

        # --- B. Separate Renamed vs New ---
        # Pattern: YYYYMMDD_Project_LAYER_TYPE_XXX.ext
        # Layers: RAW, PROC, EXP
        # Types: VID, AUD
        
        layer_abbr = "RAW"
        if layer == "processed": layer_abbr = "PROC"
        if layer == "export": layer_abbr = "EXP"
        
        type_abbr = "VID" if type_ == "video" else "AUD"
        
        # Construct the prefix
        prefix = f"{date_str.replace('-', '')}_{project_name}_{layer_abbr}_{type_abbr}_"
        
        renamed_files = []
        new_files = []
        
        for f in all_files:
            if f.name.startswith(prefix):
                renamed_files.append(f)
            else:
                new_files.append(f)
                
        # --- C. Determine Next Index ---
        max_index = 0
        for f in renamed_files:
            try:
                # Extract index from end of stem (file_001 -> 1)
                parts = f.stem.split('_')
                if parts[-1].isdigit():
                    idx = int(parts[-1])
                    if idx > max_index: max_index = idx
            except:
                continue
        current_index = max_index + 1
        
        # --- D. Sort New Files (Chronological) ---
        # We fetch metadata NOW to sort correctly before renaming
        new_files_with_meta = []
        for f in new_files:
            meta = get_file_metadata(f)
            # Use metadata date, fallback to OS modification time
            sort_key = meta['created'] or str(os.path.getmtime(f))
            new_files_with_meta.append((f, sort_key))
            
        # Sort tuple list by the date key
        new_files_with_meta.sort(key=lambda x: x[1])
        
        # --- E. Rename & Build Inventory ---
        final_list = []
        
        # 1. Add existing files to inventory
        for f in renamed_files:
            meta = get_file_metadata(f)
            final_list.append({
                "name": f.name,
                "rel_path": str(f.relative_to(project_path)),
                "meta": meta
            })
            
        # 2. Rename new files and add to inventory
        for f, _ in new_files_with_meta:
            new_name = f"{prefix}{current_index:03d}{f.suffix}"
            new_path = f.parent / new_name
            
            try:
                f.rename(new_path)
                print(f"Renamed: {f.name} -> {new_name}")
                
                # Get meta for the NEW filename
                meta = get_file_metadata(new_path)
                final_list.append({
                    "name": new_name,
                    "rel_path": str(new_path.relative_to(project_path)),
                    "meta": meta
                })
                current_index += 1
            except OSError as e:
                print(f"❌ Error renaming {f.name}: {e}")
        
        inventory[type_] = final_list
        
    return inventory

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update.py \"ProjectName\"")
        sys.exit(1)

    name_input = sys.argv[1]
    project_path = get_project_path(name_input)
    
    if not project_path:
        print(f"❌ Project containing '{name_input}' not found in {PROJECTS_ROOT}")
        sys.exit(1)

    # Parse folder name (YYYY-MM-DD_Name)
    folder_name = project_path.name
    date_part = folder_name[:10]     # 2026-02-01
    clean_name = folder_name[11:]    # MyProject

    print(f"🔄 Updating Project: {clean_name}")
    
    # Load Manifest
    manifest_path = project_path / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except:
            print("⚠️ Manifest corrupt. Creating new.")
            manifest = {"project": folder_name, "created": "", "files": {}}
    else:
        manifest = {"project": folder_name, "created": "", "files": {}}

    # PROCESS LAYERS
    file_data = {}
    has_raw = False
    has_proc = False
    has_exp = False
    
    for layer in LAYERS:
        # print(f"   Scanning {layer}...") 
        layer_data = process_layer(project_path, clean_name, date_part, layer)
        file_data[layer] = layer_data
        
        # Check if layer has content
        if layer_data['video'] or layer_data['audio']:
            if layer == 'raw': has_raw = True
            if layer == 'processed': has_proc = True
            if layer == 'export': has_exp = True

    # DETERMINE STATE
    current_state = manifest.get('state', "INIT")
    
    # Do not auto-revert an ARCHIVED state
    if current_state != "ARCHIVED":
        if has_exp:
            new_state = "EXPORTED"
        elif has_proc:
            new_state = "PROCESSED"
        elif has_raw:
            new_state = "RAW_CAPTURED"
        else:
            new_state = "INIT"
        manifest['state'] = new_state
    
    # Save Updates
    manifest['files'] = file_data
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Update Complete. State: {manifest['state']}")

if __name__ == "__main__":
    main()
