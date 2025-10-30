# FreeCAD Import.insert() Crash Issue

## Problem

The FreeCAD `Import.insert()` function causes a **segmentation fault** when importing STEP files in headless mode on some systems (particularly Railway/cloud environments).

### Symptoms
- Backend crashes completely after logging: `[Parser] Step 1.4.1: Executing Import.insert()...`
- No Python exception is caught
- Process terminates with signal 11 (SIGSEGV)
- Health check endpoint crashes when FreeCAD test runs

## Root Cause

FreeCAD attempts to initialize GUI components (Qt/X11) even in headless mode, causing segmentation faults when:
- No display is available
- Required graphics libraries are missing
- X11 dependencies are not satisfied in containerized environments

## Workarounds

### Option 1: Disable FreeCAD Health Check (Recommended for Production)

Set environment variable on Railway:

```bash
SKIP_FREECAD_HEALTH_CHECK=true
```

This disables the FreeCAD parser test in `/api/health` but still allows STEP file uploads to work.

### Option 2: Use Alternative STEP Parser

Consider using a different STEP parser library that doesn't require FreeCAD:
- `python-occ` (OpenCascade bindings)
- `cadquery` 
- `ezdxf` for 2D files
- Cloud-based CAD parsing services

### Option 3: Subprocess Isolation (Future Enhancement)

Run FreeCAD operations in a separate subprocess so crashes don't kill the main process:

```python
import subprocess
import json

def parse_step_in_subprocess(step_file_path):
    """Run FreeCAD parser in isolated subprocess"""
    result = subprocess.run(
        ['python3', 'simple_step_parser.py', step_file_path],
        capture_output=True,
        timeout=60
    )
    if result.returncode != 0:
        raise Exception(f"Parser crashed: {result.stderr}")
    return json.loads(result.stdout)
```

### Option 4: Install Additional Dependencies

Try installing additional X11 and Qt dependencies:

```dockerfile
# Railway/Docker
RUN apt-get update && apt-get install -y \
    xvfb \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxkbcommon-x11-0 \
    libdbus-1-3
```

## Current Status

✅ **Logging Added**: Comprehensive logging shows exactly where crash occurs  
✅ **Timeout Protection**: 60-second alarm to prevent hangs  
✅ **Health Check Skip**: Can disable FreeCAD test with env var  
❌ **Segfault Protection**: Cannot catch segmentation faults in Python  
⚠️ **Production Impact**: Crashes only affect STEP file upload endpoint

## Logs to Monitor

Look for these log messages to diagnose:

```
✅ Success:
[Parser] Step 1.4.1: Executing Import.insert()...
[Parser] Step 1.4.2: Import.insert() returned successfully

❌ Crash (process dies after this):
[Parser] Step 1.4.1: Executing Import.insert()...
(no Step 1.4.2 message)
```

## Recommendations

1. **Short term**: Set `SKIP_FREECAD_HEALTH_CHECK=true` on Railway
2. **Medium term**: Consider alternative STEP parsers
3. **Long term**: Implement subprocess isolation for FreeCAD operations

## Related Files

- `/backend/simple_step_parser.py` - FreeCAD parser with crash logging
- `/backend/main.py` - Health check with skip option
- Environment: Railway deployment configuration

