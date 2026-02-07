# iOS Media Pipeline

> Lightweight project orchestration for mobile video/audio production workflows

## What It Does

Manages the complete lifecycle of media projects on iOS using medallion architecture (raw → processed → export). Automatically tracks files, extracts metadata, and advances project state as you move through capture, editing, and delivery phases.

Designed for creators working across multiple apps (camera, DAW, video editor) who need deterministic file organization without manual bookkeeping.

## Key Features

- **Medallion architecture** - Clear separation between raw captures, processed edits, and final exports
- **Auto-advancing state machine** - Project state reflects file presence automatically (no manual tracking)
- **Explicit file naming** - Canonical names encode project/layer/type/sequence for self-documenting media
- **Metadata extraction** - Duration, resolution, creation time via ffprobe
- **Idempotent operations** - All scripts safe to re-run without side effects

## Quick Start

```bash
# Create new project
python3 scripts/init.py "TestProject"

# Add raw media to raw/video or raw/audio, then update
python3 scripts/update.py "TestProject"

# Check project status
python3 scripts/status.py "TestProject"

# See USER_GUIDE.md for complete workflow walkthrough
```

## Requirements

**Runtime:**
- Python 3.6+ (standard library only)
- ffprobe (from ffmpeg suite)

**Platform:**
- a-Shell on iOS (exclusive target environment)

**Installation:**
```bash
# Install ffmpeg in a-Shell (includes ffprobe)
pkg install ffmpeg

# Clone repository (a-Shell uses lg2, NOT git)
lg2 clone https://github.com/yourusername/ios-media-pipeline.git
cd ios-media-pipeline

# See USER_GUIDE.md "a-Shell Environment Setup" for SSH key configuration
```

## Project Structure

```
~/projects/YYYY-MM-DD_ProjectName/
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

## Scripts

- **init.py** - Bootstrap project structure with medallion folders
- **update.py** - Scan, rename, extract metadata, advance state
- **archive.py** - Lock project to ARCHIVED state with full inventory
- **status.py** - Display project dashboard with stats and file previews

## State Machine

Projects flow through five states automatically:

```
INIT → RAW_CAPTURED → PROCESSED → EXPORTED → ARCHIVED
```

State advances based on file presence when running `update.py`. ARCHIVED state is terminal (set manually via `archive.py`).

## File Naming Convention

Files are renamed to canonical format during updates:

```
YYYYMMDD_ProjectName_LAYER_TYPE_XXX.ext

Examples:
20260206_TestProject_RAW_VID_001.mov
20260206_TestProject_PROC_AUD_002.wav
20260206_TestProject_EXP_VID_001.mp4
```

**Components:**
- `YYYYMMDD` - Project date prefix
- `ProjectName` - Project identifier
- `LAYER` - RAW/PROC/EXP (medallion layer)
- `TYPE` - VID/AUD (media type)
- `XXX` - 3-digit sequence number

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Technical specification for AI coding agents
- **[USER_GUIDE.md](USER_GUIDE.md)** - Step-by-step project lifecycle walkthrough

## Design Philosophy

**Explicit over implicit:** State transitions are deterministic and based on observable file presence.

**Orchestration, not compute:** Scripts manage project lifecycle; external apps (camera, DAW, video editor) handle creative work.

**Human-in-the-loop:** Scripts provide structure and tracking only.

**Idempotent by design:** All operations safe to re-run, manifest is single source of truth.
