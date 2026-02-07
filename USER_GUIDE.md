# User Guide

Complete walkthrough for managing a media project from capture to archive.

---

## a-Shell Environment Setup

### What is a-Shell?

a-Shell is a terminal emulator for iOS/iPadOS that provides a Unix-like shell environment. It runs Python, ffmpeg, and other Unix tools natively on iOS using WebAssembly.

**Key characteristics:**
- Full terminal environment on iOS
- Package management via `pkg` command
- Git operations via `lg2` (libgit2), NOT standard `git`
- Sandboxed file access (~/Documents/, ~/Library/, ~/tmp/)
- Integration with iOS Files app and Shortcuts

### Critical Differences from Desktop Terminals

| Feature | Desktop Terminal | a-Shell on iOS |
|---------|------------------|----------------|
| Git command | `git` | `lg2` (libgit2) |
| File access | Entire filesystem | ~/Documents/, ~/Library/, ~/tmp/ only |
| SSH keys | ~/.ssh/ | ~/Documents/.ssh/ |
| Package manager | apt/brew/etc | `pkg install` |
| Files app | N/A | ~/Documents/ visible as "a-Shell" |

**CRITICAL:** a-Shell uses `lg2` for all git operations, NOT `git`. All git commands in this guide use `lg2`.

### First-Time Setup

**1. Install a-Shell**
- Download from iOS App Store: "a-Shell"
- Open a-Shell app

**2. Install ffmpeg (includes ffprobe)**
```bash
pkg install ffmpeg

# Verify installation
ffprobe -version
python3 --version  # Should show Python 3.11+
```

**3. (Optional) SSH Key Setup for Git Authentication**

If using SSH for git operations:

```bash
# Generate SSH key (saved to ~/Documents/.ssh/)
ssh-keygen

# Display public key to add to GitHub/GitLab
cat ~/Documents/.ssh/id_rsa.pub
```

Then add the public key to your git hosting service:
- **GitHub:** Settings → SSH and GPG keys → New SSH key
- **GitLab:** Preferences → SSH Keys → Add key

**Or use HTTPS instead:**
HTTPS authentication works with personal access tokens (no SSH setup required).

### lg2 Command Reference

**IMPORTANT:** Use `lg2` for all git operations in a-Shell, NOT `git`.

| lg2 Command | Description | Desktop Equivalent |
|-------------|-------------|-------------------|
| `lg2 clone <url>` | Clone repository | `git clone` |
| `lg2 status` | Check working tree status | `git status` |
| `lg2 add <files>` | Stage changes | `git add` |
| `lg2 commit -m "msg"` | Commit changes | `git commit` |
| `lg2 push` | Push to remote | `git push` |
| `lg2 pull` | Pull from remote | `git pull` |
| `lg2 log` | View commit history | `git log` |
| `lg2 diff` | Show changes | `git diff` |

**Authentication:**
- **SSH:** Uses keys in ~/Documents/.ssh/ (requires setup above)
- **HTTPS:** Prompts for username/token (no setup required)

### Path Sandboxing

a-Shell restricts file access to specific directories:

| Directory | Purpose | Files App Visibility |
|-----------|---------|---------------------|
| ~/Documents/ | Main working directory | Visible (appears as "a-Shell") |
| ~/projects/ | Default project location | Visible (inside ~/Documents/) |
| ~/Library/ | App data | Not visible |
| ~/tmp/ | Temporary files | Not visible |

**Important paths:**
- **Repository:** `~/Documents/ios-media-pipeline/`
- **Projects:** `~/projects/YYYY-MM-DD_ProjectName/`
- **SSH Keys:** `~/Documents/.ssh/`

**Files app integration:**
1. Open iOS Files app
2. Navigate to "On My iPhone/iPad"
3. Find "a-Shell" folder (maps to ~/Documents/)
4. Access projects, scripts, media files

### Navigation Tips

```bash
# Quick navigation commands
jump documents   # Jump to ~/Documents/
cd ~             # Home directory
cd ~/projects/   # Projects directory

# Create bookmarks for frequent locations
bookmark proj    # Create bookmark named "proj"
jump proj        # Jump to bookmarked location

# Use 'z' command for smart directory jumping (after visiting directories)
z ios-media      # Jump to ios-media-pipeline directory
```

---

## Installation

### 1. Install ffmpeg (includes ffprobe)

In a-Shell on iOS:

```bash
pkg install ffmpeg

# Verify installation
ffprobe -version
```

### 2. Clone Repository

```bash
cd ~
# a-Shell uses lg2 (NOT git) - see "a-Shell Environment Setup" above
lg2 clone https://github.com/yourusername/ios-media-pipeline.git
cd ios-media-pipeline
```

**Note:** If SSH authentication fails, use HTTPS clone or see "a-Shell Environment Setup" section for SSH key configuration.

### 3. Verify Setup

```bash
# Check Python version (3.6+ required)
python3 --version

# Test init script
python3 scripts/init.py "TestProject"
ls ~/projects/

# Clean up test
rm -rf ~/projects/*TestProject
```

---

## Complete Project Walkthrough

### Scenario: "TestProject" Project

You're creating a beach vlog with drone footage and voiceover narration.

### Step 1: Create Project

```bash
python3 scripts/init.py "TestProject"
```

**What happens:**
- Creates `~/projects/2026-02-06_TestProject/`
- Generates medallion folder structure (raw, processed, export)
- Initializes `manifest.json` with state=INIT

**Result:**
```
~/projects/2026-02-06_TestProject/
├── raw/
│   ├── video/
│   └── audio/
├── processed/
│   ├── video/
│   └── audio/
├── export/
│   ├── video/
│   └── audio/
└── manifest.json
```

### Step 2: Add Raw Media

**Using iOS Files app:**
1. Open Files app
2. Navigate to drone footage in Photos or camera roll
3. Copy video files to `~/projects/2026-02-06_TestProject/raw/video/`
4. Copy audio recordings to `~/projects/2026-02-06_TestProject/raw/audio/`

**Files can have any name at this stage:**
```
raw/video/
├── IMG_1234.MOV
├── IMG_1235.MOV
└── drone_clip.mov

raw/audio/
└── voiceover_take1.m4a
```

### Step 3: Update (Scan & Rename)

```bash
python3 scripts/update.py "TestProject"
```

**What happens:**
1. Scans `raw/video/` and `raw/audio/`
2. Renames unmapped files to canonical format
3. Extracts metadata via ffprobe (duration, resolution, creation time)
4. Updates `manifest.json` with file inventory
5. Auto-advances state: INIT → RAW_CAPTURED

**Result:**
```
raw/video/
├── 20260206_TestProject_RAW_VID_001.MOV  (was IMG_1234.MOV)
├── 20260206_TestProject_RAW_VID_002.MOV  (was IMG_1235.MOV)
└── 20260206_TestProject_RAW_VID_003.mov  (was drone_clip.mov)

raw/audio/
└── 20260206_TestProject_RAW_AUD_001.m4a  (was voiceover_take1.m4a)
```

**Manifest excerpt:**
```json
{
  "project": "2026-02-06_TestProject",
  "state": "RAW_CAPTURED",
  "files": {
    "raw": {
      "video": [
        {
          "name": "20260206_TestProject_RAW_VID_001.MOV",
          "rel_path": "raw/video/20260206_TestProject_RAW_VID_001.MOV",
          "meta": {
            "duration": 45.5,
            "resolution": "3840x2160",
            "created": "2026-02-06T10:30:00Z"
          }
        }
      ]
    }
  }
}
```

### Step 4: Check Status

```bash
python3 scripts/status.py "TestProject"
```

**Output:**
```
Project: 2026-02-06_TestProject
Created: 2026-02-06 10:30:00
State: RAW_CAPTURED

Raw Layer:
  Video: 3 files, 120.5s total, 3840x2160
    - 20260206_TestProject_RAW_VID_001.MOV (45.5s, 3840x2160)
    - 20260206_TestProject_RAW_VID_002.MOV (30.0s, 3840x2160)
  Audio: 1 file, 180.0s total
    - 20260206_TestProject_RAW_AUD_001.m4a (180.0s)

Processed Layer: (empty)
Export Layer: (empty)
```

### Step 5: Edit in External App

**In LumaFusion (or your video editor):**
1. Open LumaFusion
2. Import files from `~/projects/2026-02-06_TestProject/raw/`
3. Edit timeline (cut, color grade, add effects)
4. Export edited clips to `~/projects/2026-02-06_TestProject/processed/video/`

**Example exports:**
- Intro sequence → copy to `processed/video/` (any filename)
- Main sequence → copy to `processed/video/`
- Outro sequence → copy to `processed/video/`

### Step 6: Update Again (Processed Stage)

```bash
python3 scripts/update.py "TestProject"
```

**What happens:**
1. Scans `processed/video/` and `processed/audio/`
2. Renames new files to canonical format (PROC layer)
3. Extracts metadata
4. Auto-advances state: RAW_CAPTURED → PROCESSED

**Result:**
```
processed/video/
├── 20260206_TestProject_PROC_VID_001.mp4
├── 20260206_TestProject_PROC_VID_002.mp4
└── 20260206_TestProject_PROC_VID_003.mp4
```

**Status now shows:**
```bash
python3 scripts/status.py "TestProject"

# Output includes:
State: PROCESSED
Processed Layer:
  Video: 3 files, 240.0s total
```

### Step 7: Final Export

**In LumaFusion:**
1. Assemble final deliverable from processed clips
2. Export full video to `~/projects/2026-02-06_TestProject/export/video/`

**Files can have any name:**
```
export/video/
└── TestProject_Final_4K.mp4
```

### Step 8: Update & Archive

```bash
# Update to rename export and advance state
python3 scripts/update.py "TestProject"

# State is now: EXPORTED
python3 scripts/status.py "TestProject"

# Archive project (locks state)
python3 scripts/archive.py "TestProject"
```

**What happens:**
1. `update.py` renames export file to `20260206_TestProject_EXP_VID_001.mp4`
2. State advances: PROCESSED → EXPORTED
3. `archive.py` locks state to ARCHIVED
4. Generates `README_ARCHIVE.txt` with full inventory

**README_ARCHIVE.txt preview:**
```
Project: 2026-02-06_TestProject
Archived: 2026-02-06 15:45:00
State: ARCHIVED

=== INVENTORY ===

Raw Layer:
  Video: 3 files, 120.5s
  Audio: 1 file, 180.0s

Processed Layer:
  Video: 3 files, 240.0s

Export Layer:
  Video: 1 file, 480.0s
    - 20260206_TestProject_EXP_VID_001.mp4 (480.0s, 3840x2160)
```

**State is now locked:**
```bash
python3 scripts/status.py "TestProject"

# Output:
State: ARCHIVED (locked)
```

---

## File Naming Convention

### Pattern

```
YYYYMMDD_ProjectName_LAYER_TYPE_XXX.ext
```

### Components

- **YYYYMMDD**: Project creation date (from folder name)
- **ProjectName**: Project identifier
- **LAYER**: Medallion layer
  - `RAW` - Raw captures (camera, mic)
  - `PROC` - Processed edits (editor exports)
  - `EXP` - Final exports (deliverables)
- **TYPE**: Media type
  - `VID` - Video files
  - `AUD` - Audio files
- **XXX**: 3-digit sequence number (001, 002, 003...)
- **ext**: Original file extension (preserved)

### Examples

```
20260206_TestProject_RAW_VID_001.MOV    # Raw drone footage
20260206_TestProject_RAW_AUD_001.m4a    # Raw voiceover
20260206_TestProject_PROC_VID_001.mp4   # Edited intro sequence
20260206_TestProject_EXP_VID_001.mp4    # Final deliverable
```

---

## State Machine

### States

1. **INIT** - Project created, empty folders
2. **RAW_CAPTURED** - Raw media ingested
3. **PROCESSED** - Edited files exported from editor
4. **EXPORTED** - Final deliverable ready
5. **ARCHIVED** - Project locked, inventory documented

### Transitions (Auto-advancing)

```
INIT
  ↓ (auto: when raw/ has files)
RAW_CAPTURED
  ↓ (auto: when processed/ has files)
PROCESSED
  ↓ (auto: when export/ has files)
EXPORTED
  ↓ (manual: archive.py)
ARCHIVED (locked)
```

**Key behaviors:**
- State advances automatically during `update.py` based on file presence
- ARCHIVED state is sticky (won't revert even if files removed)
- State only moves forward, never backward

---

## Troubleshooting

### git: command not found

**Error:**
```
bash: git: command not found
```

**Reason:** a-Shell uses `lg2` (libgit2) instead of `git` for version control.

**Solution:**
Replace all git commands with lg2:
```bash
lg2 clone <url>    # Instead of: git clone
lg2 status         # Instead of: git status
lg2 add <files>    # Instead of: git add
lg2 commit -m "msg"  # Instead of: git commit
```

See "a-Shell Environment Setup" section for full lg2 command reference.

### SSH authentication failed

**Error:**
```
Permission denied (publickey)
fatal: Could not read from remote repository
```

**Solution:**

**Option 1: Generate and configure SSH key**
```bash
# Generate SSH key in a-Shell
ssh-keygen

# Display public key
cat ~/Documents/.ssh/id_rsa.pub
```

Copy the public key output and add to your git hosting service:
- **GitHub:** Settings → SSH and GPG keys → New SSH key
- **GitLab:** Preferences → SSH Keys → Add key

**Option 2: Use HTTPS instead**
```bash
# Clone with HTTPS (no SSH key needed)
lg2 clone https://github.com/yourusername/ios-media-pipeline.git
```

When prompted, use:
- **Username:** Your git username
- **Password:** Personal access token (NOT your account password)

### ffprobe not found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffprobe'
```

**Solution:**
```bash
pkg install ffmpeg
ffprobe -version  # Verify
```

### State not advancing

**Problem:** Ran `update.py` but state still INIT

**Check:**
1. Files actually in correct folder?
   ```bash
   ls ~/projects/YYYY-MM-DD_ProjectName/raw/video/
   ```
2. Files renamed during update?
   - Look for `YYYYMMDD_ProjectName_RAW_VID_XXX.*` pattern

**Solution:** State only advances if files exist in expected folders

### File not renamed

**Problem:** File still has original name after `update.py`

**Reason:** File already matches canonical pattern (was previously renamed)

**Behavior:** `update.py` only renames unmapped files

### Can't re-run update.py

**Problem:** Worried about running update.py multiple times

**Solution:** All scripts are idempotent (safe to re-run). Files already in canonical format are skipped.

---

## FAQ

### Can I rename files manually?

Yes, but follow the canonical pattern exactly. Otherwise `update.py` will rename them again.

### What if I delete manifest.json?

Run `update.py` - it will create a new manifest with state=INIT and scan all folders.

### Can I add files after archiving?

Yes, but state stays ARCHIVED (won't advance). To update inventory, re-run `update.py` after archive.

### Do I need to use all three layers?

No. You can skip processed layer and export directly from raw. State machine will jump states accordingly.

### Can I move projects between devices?

Yes. Copy entire project folder (including manifest.json). Run `update.py` on new device to verify paths.

### What if ffprobe fails on a file?

File is still renamed and added to manifest, but metadata fields will be null.

---

