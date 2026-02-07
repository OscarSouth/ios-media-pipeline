# iOS Media Pipeline - Technical Specification

**Directive:** Be radically precise. No fluff. Pure information only.

**Platform:** a-Shell on iOS (exclusive)
**Runtime:** Python 3.6+
**Dependencies:** ffprobe (external binary)

---

## Project Overview

Deterministic project management for mobile video/audio production using medallion architecture (raw → processed → export) with auto-advancing state machine and explicit file naming.

**Problem Solved:** Mobile content creation lacks project boundaries, state tracking, and automated file management. Raw media scattered across Photos app with no audit trail.

**Solution:** Organize projects as YYYY-MM-DD_ProjectName folders with manifest-driven state tracking, automatic file renaming, and metadata extraction.

---

## Architecture

### Medallion Layers
```
raw/          Bronze tier - original captures
  ├── video/
  └── audio/
processed/    Silver tier - edited versions
  ├── video/
  └── audio/
export/       Gold tier - final deliverables
  ├── video/
  └── audio/
```

### State Machine
```
INIT
  ↓ (auto: if raw files exist)
RAW_CAPTURED
  ↓ (auto: if processed files exist)
PROCESSED
  ↓ (auto: if export files exist)
EXPORTED
  ↓ (manual: archive.py)
ARCHIVED (terminal, sticky)
```

**State Advancement:** Automatic via `update.py` based on file presence. ARCHIVED state never reverts.

### File Naming Convention

**Pattern:** `YYYYMMDD_ProjectName_LAYER_TYPE_XXX.ext`

| Component | Values | Example |
|-----------|--------|---------|
| YYYYMMDD | Date prefix from project | 20260206 |
| ProjectName | Project identifier | TestProject |
| LAYER | RAW/PROC/EXP | RAW |
| TYPE | VID/AUD | VID |
| XXX | 3-digit sequence | 001 |

**Examples:**
- `20260206_TestProject_RAW_VID_001.mov`
- `20260206_TestProject_PROC_AUD_002.wav`
- `20260206_TestProject_EXP_VID_001.mp4`

### Manifest Structure

```json
{
  "project": "2026-02-06_TestProject",
  "created": "2026-02-06T10:30:00Z",
  "state": "EXPORTED",
  "files": {
    "raw": {
      "video": [{
        "name": "20260206_TestProject_RAW_VID_001.mov",
        "rel_path": "raw/video/20260206_TestProject_RAW_VID_001.mov",
        "meta": {
          "duration": 45.5,
          "created": "2026-02-06T10:30:00Z",
          "resolution": "3840x2160"
        }
      }],
      "audio": []
    },
    "processed": { "video": [], "audio": [] },
    "export": { "video": [], "audio": [] }
  }
}
```

**Metadata Fields:**
- `duration`: Seconds (float)
- `created`: ISO8601 timestamp
- `resolution`: "WIDTHxHEIGHT" string

**No Schema Validation:** Removed for simplicity (was: jsonschema validation in previous version).

---

## Scripts Reference

### init.py

**Purpose:** Bootstrap new project structure

**Usage:**
```bash
python3 scripts/init.py "ProjectName"
```

**Creates:**
- `~/projects/2026-02-06_ProjectName/` directory
- Medallion folder structure (raw, processed, export with video/audio subdirs)
- `manifest.json` with state=INIT

**Output:** Project path printed to stdout

---

### update.py

**Purpose:** Scan directories, rename unmapped files, extract metadata, advance state

**Usage:**
```bash
python3 scripts/update.py "ProjectName"
```

**Operations:**
1. Recursively scan raw/, processed/, export/
2. Identify unmapped files (not in manifest)
3. Sort new files chronologically by creation time
4. Rename to pattern: YYYYMMDD_Project_LAYER_TYPE_XXX.ext
5. Extract metadata via ffprobe (duration, resolution, creation_time)
6. Update manifest file inventory
7. Auto-advance state based on file presence

**State Advancement Logic:**
```python
if state == "INIT" and raw_files_exist:
    state = "RAW_CAPTURED"
if state == "RAW_CAPTURED" and processed_files_exist:
    state = "PROCESSED"
if state == "PROCESSED" and export_files_exist:
    state = "EXPORTED"
if state == "ARCHIVED":
    # Never revert ARCHIVED state
    pass
```

**ffprobe Integration:**
- Extracts: duration (seconds), creation_time (ISO8601), width/height (resolution)
- Falls back gracefully if ffprobe fails (no metadata stored)
- Command: `ffprobe -v quiet -print_format json -show_format -show_streams <file>`

**Idempotent:** Safe to re-run (skips already mapped files)

---

### archive.py

**Purpose:** Lock project to ARCHIVED state, generate human-readable inventory

**Usage:**
```bash
python3 scripts/archive.py "ProjectName"
```

**Operations:**
1. Validate export/ directory has files (warn if empty, prompt to continue)
2. Set state to ARCHIVED (terminal state)
3. Generate `README_ARCHIVE.txt` with full inventory:
   - Project name, created date, state
   - Per-layer file counts, total duration, resolution summary
   - File list with metadata

**Archive README Format:**
```
Project: 2026-02-06_TestProject
Created: 2026-02-06T10:30:00Z
Status: ARCHIVED

=== RAW ===
Video: 3 files, 2m 15s, 3840x2160
- 20260206_TestProject_RAW_VID_001.mov (45s, 3840x2160)
...
```

---

### status.py

**Purpose:** Display project dashboard with metadata aggregation

**Usage:**
```bash
python3 scripts/status.py "ProjectName"
```

**Output:**
```
Project: 2026-02-06_TestProject
Created: 2026-02-06T10:30:00Z
State: EXPORTED

=== RAW ===
Video: 3 files, 2m 15s
- 20260206_TestProject_RAW_VID_001.mov (3840x2160)
- 20260206_TestProject_RAW_VID_002.mov (3840x2160)
(+1 more...)

Audio: 1 file, 2m 10s
...

Total Duration: 6m 45s
```

**Displays:**
- Project name, creation date, current state
- Per-layer file counts and total durations
- First 2 files per layer with resolution
- Indicator if more files exist
- Total project duration across all layers

---

## Design Decisions

### Why Medallion Architecture?
**Reason:** Separates capture, editing, delivery into explicit stages
**Benefit:** Clear project phase boundaries, prevents accidental overwrites

### Why Auto-Advancing State Machine?
**Reason:** State reflects file presence automatically, no manual management
**Benefit:** Enforces workflow order (raw → processed → export)

### Why CLI Args Only?
**Reason:** a-Shell compatibility, simpler automation

### Why ffprobe Dependency?
**Reason:** Reliable video/audio metadata extraction
**Alternative:** PIL (limited format support), moviepy (large dependency)
**Trade-off:** External binary required

---

## Implementation Details

### Project Directory Structure
```
~/projects/
└── 2026-02-06_TestProject/
    ├── raw/
    │   ├── video/
    │   │   └── 20260206_TestProject_RAW_VID_001.mov
    │   └── audio/
    ├── processed/
    │   ├── video/
    │   └── audio/
    ├── export/
    │   ├── video/
    │   └── audio/
    ├── manifest.json
    └── README_ARCHIVE.txt (after archive.py)
```

### ffprobe Metadata Extraction

**Command:**
```bash
ffprobe -v quiet -print_format json -show_format -show_streams <file>
```

**Parsed Fields:**
- `format.duration` → float (seconds)
- `format.tags.creation_time` → ISO8601 string
- `streams[0].width` / `streams[0].height` → resolution string

**Error Handling:** Silent fail (no metadata if ffprobe unavailable)

### File Sorting Logic

**Chronological by Creation Time:**
1. Extract OS stat creation time: `os.stat(file).st_ctime`
2. Fall back to modification time: `os.stat(file).st_mtime`
3. Sort ascending (oldest first)
4. Assign sequence numbers: 001, 002, 003...

**Purpose:** Maintains capture order in file naming

---

## Requirements

**Python:** 3.6+ (stdlib: json, subprocess, pathlib, os, re, argparse, datetime)
**ffprobe:** External binary (from ffmpeg suite)
**Platform:** a-Shell on iOS (exclusive target)

**Installation (a-Shell):**
```bash
# Install ffmpeg (includes ffprobe)
pkg install ffmpeg

# Verify
ffprobe -version
```

**Git Operations (a-Shell):**
- Use `lg2` command (NOT `git`) for all version control operations
- SSH keys stored in: ~/Documents/.ssh/
- HTTPS clone alternative available (no SSH setup required)
- See USER_GUIDE.md "a-Shell Environment Setup" for complete lg2 workflow

---

