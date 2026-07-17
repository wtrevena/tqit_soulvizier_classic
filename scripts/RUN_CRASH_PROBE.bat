@echo off
REM ====================================================================
REM  RUN_CRASH_PROBE.bat - one double-click blood-cave crash probe.
REM
REM  What it does: attaches a READ-ONLY Frida probe to a running TQ.exe
REM  and logs each navmesh chamber as it streams in. When the game
REM  crashes, the last chamber that loaded but never finished = the
REM  culprit. It NEVER launches, kills, or restarts TQ or Steam; it only
REM  watches an already-running game and detaches cleanly.
REM
REM  Just double-click this file. Then launch TQ via Steam and play to
REM  the crash. It RE-ARMS automatically after each crash, so you can keep
REM  relaunching and playing - every crash is logged. Press Ctrl+C in this
REM  window to stop. Logs land in local\crash_probe\ (one file per crash).
REM ====================================================================
setlocal
set "PYTHONIOENCODING=utf-8"

REM Repo root = the folder ABOVE this script (scripts\ -> repo).
cd /d "%~dp0.."

echo.
echo ============================================================
echo  TQ BLOOD-CAVE CRASH PROBE  (read-only, attach-only)
echo ============================================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] The 'py' Python launcher was not found on PATH.
  echo         Install Python 3 from python.org, then run the probe manually:
  echo             py scripts\crash_probe\run_crash_probe.py
  echo.
  pause
  exit /b 1
)

py scripts\crash_probe\run_crash_probe.py --loop %*
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
echo  Probe finished (exit code %RC%). This window stays open so
echo  you can copy the FULL LOG path printed above.
echo  Logs live in:  local\crash_probe\
echo ============================================================
echo.
pause
endlocal
