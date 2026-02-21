#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$REPO_ROOT/local"
CONFIG_FILE="$CONFIG_DIR/config.env"
mkdir -p "$CONFIG_DIR"

ok=0
warn=0
fail=0

pass()  { echo "  [OK]   $1"; ((ok++)) || true; }
skip()  { echo "  [WARN] $1"; ((warn++)) || true; }
die()   { echo "  [FAIL] $1"; ((fail++)) || true; }

echo "=== SoulvizierClassic Doctor ==="
echo ""

# ── Windows username ────────────────────────────────────────────────
WIN_USER="$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n' || true)"
if [[ -z "$WIN_USER" ]]; then
    die "Could not determine Windows username"
else
    pass "Windows user: $WIN_USER"
fi

# ── Documents path (handle OneDrive redirect) ──────────────────────
WIN_DOCS=""
for candidate in \
    "/mnt/c/Users/$WIN_USER/OneDrive/Documents" \
    "/mnt/c/Users/$WIN_USER/Documents"; do
    if [[ -d "$candidate" ]]; then
        WIN_DOCS="$candidate"
        break
    fi
done
if [[ -z "$WIN_DOCS" ]]; then
    die "Could not find Windows Documents folder"
else
    pass "Documents: $WIN_DOCS"
fi

# ── TQ IT documents base ───────────────────────────────────────────
TQ_DOCS_BASE=""
for candidate in \
    "$WIN_DOCS/My Games/Titan Quest - Immortal Throne" \
    "$WIN_DOCS/My Games/Titan Quest"; do
    if [[ -d "$candidate" ]]; then
        TQ_DOCS_BASE="$candidate"
        break
    fi
done
if [[ -z "$TQ_DOCS_BASE" ]]; then
    die "Could not find Titan Quest documents folder"
else
    pass "TQ docs base: $TQ_DOCS_BASE"
fi

# ── CustomMaps path ────────────────────────────────────────────────
WIN_CUSTOMMAPS="$TQ_DOCS_BASE/CustomMaps"
if [[ -d "$WIN_CUSTOMMAPS" ]]; then
    pass "CustomMaps folder exists: $WIN_CUSTOMMAPS"
else
    skip "CustomMaps folder not found, will create on deploy: $WIN_CUSTOMMAPS"
fi

# ── Working path ───────────────────────────────────────────────────
WIN_WORKING="$TQ_DOCS_BASE/Working"
if [[ -d "$WIN_WORKING" ]]; then
    pass "Working folder exists: $WIN_WORKING"
else
    skip "Working folder not found: $WIN_WORKING (may be needed for ArtManager)"
fi

# ── TQAE install path ─────────────────────────────────────────────
TQAE_ROOT=""

find_tqae_in_library() {
    local lib="$1"
    local path="$lib/steamapps/common/Titan Quest Anniversary Edition"
    if [[ -d "$path" && -f "$path/TQ.exe" ]]; then
        echo "$path"
        return 0
    fi
    return 1
}

# Check default Steam library
DEFAULT_STEAM="/mnt/c/Program Files (x86)/Steam"
if result="$(find_tqae_in_library "$DEFAULT_STEAM")"; then
    TQAE_ROOT="$result"
fi

# If not found, parse libraryfolders.vdf for alternate libraries
if [[ -z "$TQAE_ROOT" ]]; then
    VDF="$DEFAULT_STEAM/steamapps/libraryfolders.vdf"
    if [[ -f "$VDF" ]]; then
        while IFS= read -r line; do
            lib_path="$(echo "$line" | grep -oP '"path"\s+"\K[^"]+' || true)"
            if [[ -n "$lib_path" ]]; then
                wsl_path="/mnt/$(echo "$lib_path" | sed 's|\\\\|/|g; s|^\([A-Za-z]\):|/\L\1|')"
                if result="$(find_tqae_in_library "$wsl_path")"; then
                    TQAE_ROOT="$result"
                    break
                fi
            fi
        done < "$VDF"
    fi
fi

if [[ -z "$TQAE_ROOT" ]]; then
    die "Could not find Titan Quest Anniversary Edition install"
else
    pass "TQAE install: $TQAE_ROOT"
fi

# ── ArchiveTool ────────────────────────────────────────────────────
TQ_ARCHIVETOOL=""
if [[ -n "$TQAE_ROOT" && -f "$TQAE_ROOT/ArchiveTool.exe" ]]; then
    TQ_ARCHIVETOOL="$TQAE_ROOT/ArchiveTool.exe"
    pass "ArchiveTool: $TQ_ARCHIVETOOL"
else
    skip "ArchiveTool.exe not found"
fi

# ── ArtManager ─────────────────────────────────────────────────────
TQ_ARTMANAGER=""
if [[ -n "$TQAE_ROOT" && -f "$TQAE_ROOT/ArtManager.exe" ]]; then
    TQ_ARTMANAGER="$TQAE_ROOT/ArtManager.exe"
    pass "ArtManager: $TQ_ARTMANAGER"
else
    skip "ArtManager.exe not found"
fi

# ── Steam Workshop for TQAE (app 475150) ──────────────────────────
STEAM_WORKSHOP_475150=""
for steam_root in "$DEFAULT_STEAM" "/mnt/c/Program Files/Steam"; do
    candidate="$steam_root/steamapps/workshop/content/475150"
    if [[ -d "$candidate" ]]; then
        STEAM_WORKSHOP_475150="$candidate"
        break
    fi
done
if [[ -z "$STEAM_WORKSHOP_475150" ]]; then
    skip "Workshop folder for TQAE not found"
else
    mod_count="$(ls "$STEAM_WORKSHOP_475150" 2>/dev/null | wc -l)"
    pass "Workshop (475150): $STEAM_WORKSHOP_475150 ($mod_count mod(s))"
fi

# ── SteamCMD ───────────────────────────────────────────────────────
STEAMCMD_EXE=""
for candidate in "/mnt/c/steamcmd/steamcmd.exe" "/mnt/c/SteamCMD/steamcmd.exe"; do
    if [[ -f "$candidate" ]]; then
        STEAMCMD_EXE="$candidate"
        break
    fi
done
if [[ -z "$STEAMCMD_EXE" ]]; then
    skip "SteamCMD not found (needed later for Workshop upload)"
else
    pass "SteamCMD: $STEAMCMD_EXE"
fi

# ── WSL2 tools ─────────────────────────────────────────────────────
echo ""
echo "--- WSL2 tool check ---"
for tool in unzip 7z rsync python3 pip3 dos2unix; do
    if command -v "$tool" &>/dev/null; then
        pass "$tool: $(command -v "$tool")"
    else
        skip "$tool not found (install with: sudo apt install ...)"
    fi
done

# ── Write config.env ───────────────────────────────────────────────
echo ""
echo "--- Writing config ---"

cat > "$CONFIG_FILE" <<ENVEOF
# Auto-generated by doctor.sh — $(date -Iseconds)
WIN_USER=$WIN_USER
WIN_DOCS=$WIN_DOCS
TQ_DOCS_BASE=$TQ_DOCS_BASE
WIN_CUSTOMMAPS=$WIN_CUSTOMMAPS
WIN_WORKING=$WIN_WORKING
TQAE_ROOT=$TQAE_ROOT
TQ_ARCHIVETOOL=$TQ_ARCHIVETOOL
TQ_ARTMANAGER=$TQ_ARTMANAGER
STEAM_WORKSHOP_475150=$STEAM_WORKSHOP_475150
STEAMCMD_EXE=$STEAMCMD_EXE
ENVEOF

pass "Config written to $CONFIG_FILE"

# ── Summary ────────────────────────────────────────────────────────
echo ""
echo "=== Summary: $ok OK, $warn WARN, $fail FAIL ==="

if [[ "$fail" -gt 0 ]]; then
    echo "FATAL: $fail critical check(s) failed. Fix the above and re-run."
    exit 1
fi

if [[ "$warn" -gt 0 ]]; then
    echo "Some optional items missing — see warnings above."
fi

echo "Doctor complete."
exit 0
