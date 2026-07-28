#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_crash_probe.py - attach the RLTD navmesh crash probe to a RUNNING TQ.exe.

P0-C blood-cave crash harness. Dossier: docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md
sec 7.2. Guide: docs/crash/WILL_CRASH_PROBE_GUIDE.md.

READ-ONLY and NON-INVASIVE:
  * It ATTACHES to an already running TQ.exe by name. It never spawns TQ.exe and
    it NEVER kills it. Detaching (Ctrl+C, or the game exiting) leaves the game
    untouched - Frida attach/detach does not terminate the target.
  * The Frida agent (rltd_crash_probe.js) only OBSERVES: it reads registers and
    memory and logs. It patches nothing.

WHAT YOU GET
  A timestamped log under local/crash_probe/. For every navmesh load the engine
  performs it records: which blood-cave chamber (GUID -> name), the co-resident
  chambers at that instant (tests hypothesis H1), ENTER/LEAVE of ProcessRLTD, and
  (optionally) the per-tile allocation / memcpy sizes. If TQ.exe CRASHES, the
  Frida session detaches and this runner prints the LAST navmesh load that logged
  ENTER with no LEAVE = the corrupting chamber (dossier sec 7.2 step 3).

USAGE (attach to a running game):
    set PYTHONIOENCODING=utf-8
    py scripts\\crash_probe\\run_crash_probe.py

OFFLINE VALIDATION (no game, does NOT attach to anything):
    py scripts\\crash_probe\\run_crash_probe.py --self-test
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

REPO = Path(__file__).resolve().parents[2]
JS_PATH = REPO / 'scripts' / 'crash_probe' / 'rltd_crash_probe.js'
OUT_DIR = REPO / 'local' / 'crash_probe'
LOCK_PATH = OUT_DIR / 'probe.lock'
sys.path.insert(0, str(REPO / 'tools'))


def _pid_alive(pid):
    """True if a process with this pid exists (Windows: tasklist filter)."""
    try:
        import subprocess
        out = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/NH'],
                             capture_output=True, text=True, timeout=15).stdout
        return str(pid) in out
    except Exception:
        return True   # cannot tell -> assume alive (fail safe: refuse to start a second probe)


def acquire_single_instance_lock():
    """Refuse to run if another probe is already live.

    Two probes attaching to the same TQ.exe install duplicate Interceptor hooks at
    the same engine addresses. That destabilises a 32-bit target and can crash the
    game on startup - it did on 2026-07-27, when stale waiting probes from earlier
    launches all attached at once. One probe, always.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            holder = int(LOCK_PATH.read_text(encoding='utf-8').split()[0])
        except Exception:
            holder = None
        if holder and holder != os.getpid() and _pid_alive(holder):
            raise SystemExit(
                f"ANOTHER CRASH PROBE IS ALREADY RUNNING (pid {holder}).\n"
                f"Two probes hooking the same TQ.exe can crash the game. Stop that one first\n"
                f"(taskkill /PID {holder} /F), or delete {LOCK_PATH} if it is stale.")
        LOCK_PATH.unlink(missing_ok=True)   # stale lock from a dead probe
    LOCK_PATH.write_text(f"{os.getpid()}\n", encoding='utf-8')


def release_single_instance_lock():
    try:
        if LOCK_PATH.exists() and LOCK_PATH.read_text(encoding='utf-8').split()[0] == str(os.getpid()):
            LOCK_PATH.unlink()
    except Exception:
        pass

# Tiers -> which hot hooks the agent installs. The chamber-identity signal (the
# decisive datum) is captured at every tier; the tiers differ only in the
# per-tile size logging, whose hooks fire on hot paths.
#   chambers : gate + ProcessRLTD enter/leave + co-residency         (lightest, most timing-faithful)
#   allocs   : + per-tile alloc sizes  (DEFAULT; alloc hook, modest overhead)
#   full     : + per-tile memcpy sizes (memcpy is the hottest path; use only if needed)
TIERS = {
    'chambers': {'alloc': False, 'memcpy': False},
    'allocs':   {'alloc': True,  'memcpy': False},
    'full':     {'alloc': True,  'memcpy': True},
}


def discover_map(explicit):
    """Find the deployed CustomMaps Levels.arc. Prefer the DEV entry (Will plays DEV)."""
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise SystemExit(f"--map not found: {p}")
        return p
    home = Path(os.environ.get('USERPROFILE', str(Path.home())))
    roots = [home / 'OneDrive' / 'Documents' / 'My Games', home / 'Documents' / 'My Games']
    games = ['Titan Quest - Immortal Throne', 'Titan Quest Anniversary Edition']
    mods = ['SoulvizierClassicDEV', 'SoulvizierClassic']  # DEV first
    for root in roots:
        for game in games:
            for m in mods:
                p = root / game / 'CustomMaps' / m / 'Resources' / 'Levels.arc'
                if p.is_file():
                    return p
    for root in roots:
        if not root.is_dir():
            continue
        hits = sorted(root.glob('Titan Quest*/CustomMaps/SoulvizierClassic*/Resources/Levels.arc'),
                      key=lambda x: (0 if 'DEV' in x.parts[-3] else 1, str(x)))
        if hits:
            return hits[0]
    raise SystemExit(
        "Could not find a deployed SoulvizierClassic[DEV] Levels.arc under My Games\\...\\CustomMaps.\n"
        "Pass one explicitly:  --map \"<path to CustomMaps\\SoulvizierClassicDEV\\Resources\\Levels.arc>\"")


def build_name_maps(map_path):
    """Parse the deployed map's LEVELS section: index->name, guid->name, cluster set.
    Reuses the exact proven logic from tools/debug/frida_probe.py."""
    from arc_patcher import ArcArchive
    from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
    arc = ArcArchive.from_file(map_path)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    names, guid2name, cluster = [], {}, set()
    for lv in parse_level_index(data, sec[SEC_LEVELS]):
        key = lv['fname'].replace('\\', '/').lower()
        base = key.split('/')[-1].replace('.lvl', '')
        names.append(base)
        guid2name[lv['ints_raw'][36:52].hex()] = base
        if 'xbloodcave' in key or base == 'random09a':
            cluster.add(base)
    return names, guid2name, sorted(cluster)


def render_script(names, guid2name, cluster, cfg):
    """Prepend the injected-globals header to the standalone JS agent."""
    body = JS_PATH.read_text(encoding='utf-8')
    header = (
        "// ---- injected by run_crash_probe.py (deployed-map derived) ----\n"
        f"const PROBE_NAMES = {json.dumps(names)};\n"
        f"const PROBE_GUIDMAP = {json.dumps(guid2name)};\n"
        f"const PROBE_CLUSTER = {json.dumps(cluster)};\n"
        f"const PROBE_CFG = {json.dumps(cfg)};\n"
        "// ---------------------------------------------------------------\n"
    )
    return header + body


class Probe:
    """Decodes agent messages, streams the log, and tracks ENTER-with-no-LEAVE."""

    def __init__(self, logf):
        self.logf = logf
        self.open = {}       # seq -> load record still in ProcessRLTD (no LEAVE yet)
        self.detached = None    # set to reason string when the session detaches

    def out(self, s):
        line = time.strftime('%H:%M:%S ') + s
        print(line, flush=True)
        self.logf.write(line + '\n')
        self.logf.flush()

    def fileonly(self, s):
        self.logf.write('           ' + s + '\n')
        self.logf.flush()

    def tail_lines(self, n):
        """Return the last n lines of the log (flushes first so the crash tail is included)."""
        try:
            self.logf.flush()
        except Exception:
            pass
        try:
            with open(self.logf.name, 'r', encoding='utf-8') as f:
                return f.read().splitlines()[-n:]
        except Exception:
            return []

    def on_message(self, msg, _data):
        if msg.get('type') == 'error':
            self.out('JS ERROR: ' + msg.get('description', '') + '  ' + json.dumps(msg.get('stack', '')[:400]))
            return
        p = msg.get('payload') or {}
        t = p.get('t')
        if t == 'ready':
            arch = p.get('arch')
            self.out(f"[ready] Engine.dll base={p['base']} arch={arch} ptr={p['pointerSize']}B "
                     f"levels={p['levels']} cluster={p['cluster']} cfg={p['cfg']}")
            self.out(f"        GATE={p['gate']} ProcessRLTD={p['procrltd']}")
            if arch != 'ia32':
                self.out(f"        WARNING: target arch is '{arch}', expected 'ia32' (32-bit TQ.exe). "
                         f"VAs assume the 32-bit Engine.dll; results may be wrong.")
            else:
                self.out("        cross-bitness OK: 32-bit target instrumented from 64-bit Python.")
        elif t == 'info':
            self.out('[info] ' + p['m'])
        elif t == 'warn':
            self.out('[warn] ' + p['m'])
        elif t == 'gate':
            self._log_gate(p)
        elif t == 'enter':
            resident = p.get('resident')
            rec = {'lvl': p['lvl'], 'cluster': p['cluster'], 'deps': p.get('deps') or [],
                   'guid': p.get('guid'), 'payload': p.get('payload'),
                   'resident': resident,
                   'alloc': {'n': 0, 'min': None, 'max': None, 'sum': 0},
                   'memcpy': {'n': 0, 'min': None, 'max': None, 'sum': 0}}
            self.open[p['seq']] = rec
            cres = [r['nm'] for r in (resident or []) if r.get('cluster')]
            flag = '  <<< BLOOD-CAVE CLUSTER' if p['cluster'] else ''
            self.out(f"ENTER #{p['seq']:<4d} {p['lvl']:<34s} deps={p.get('deps')} "
                     f"co-resident-cluster={cres}{flag}")
            if p['cluster'] or cres:
                self.fileonly('full-resident: ' + ', '.join(
                    f"{r['i']}:{r['nm']}(navOK={r['navOK']})" for r in (resident or [])))
        elif t == 'alloc':
            self._acc(p, 'alloc')
        elif t == 'memcpy':
            self._acc(p, 'memcpy')
        elif t == 'leave':
            rec = self.open.pop(p['seq'], None)
            ok = 'OK' if p.get('ok') else 'REJECTED'
            mark = '' if p.get('ok') else '   <<< REJECTED'
            flag = '  [cluster]' if p['cluster'] else ''
            extra = self._size_summary(rec) if rec else ''
            self.out(f"LEAVE #{p['seq']:<4d} {p['lvl']:<34s} {ok} (al={p.get('al')}){flag}{extra}{mark}")

    def _acc(self, p, kind):
        rec = self.open.get(p.get('seq'))
        if not rec:
            return
        a = rec[kind]
        sz = p.get('size')
        a['n'] += 1
        if isinstance(sz, int):
            a['sum'] += sz
            a['min'] = sz if a['min'] is None else min(a['min'], sz)
            a['max'] = sz if a['max'] is None else max(a['max'], sz)

    @staticmethod
    def _size_summary(rec):
        parts = []
        for kind in ('alloc', 'memcpy'):
            a = rec[kind]
            if a['n']:
                parts.append(f"{kind}={a['n']}(min={a['min']},max={a['max']},sum={a['sum']})")
        return ('  ' + ' '.join(parts)) if parts else ''

    def _log_gate(self, p):
        # Pre-call chamber identity (co-residency is captured at ProcessRLTD entry instead).
        flag = '  <<< BLOOD-CAVE CLUSTER' if p['cluster'] else ''
        self.out(f"GATE  #{p['seq']:<4d} load={p['lvl']:<34s} edi={p.get('edi')} "
                 f"guid={p.get('guid')}{flag}")

    def crash_summary(self, reason):
        open_loads = dict(self.open)   # snapshot: the agent thread may still be delivering messages
        self.out('=' * 78)
        if open_loads:
            self.out(f"SESSION DETACHED (reason={reason}). {len(open_loads)} navmesh load(s) had "
                     f"ENTER with NO LEAVE:")
            for seq in sorted(open_loads):
                rec = open_loads[seq]
                star = '  <<<<<< PRIME CRASH SUSPECT' if rec['cluster'] else ''
                self.out(f"  ENTER #{seq} {rec['lvl']}  (guid={rec['guid']})"
                         f"  deps={rec['deps']}{star}")
                self.out(f"      {self._size_summary(rec).strip() or 'no per-tile size samples'}")
                if rec.get('resident') is not None:
                    cres = [r['nm'] for r in rec['resident'] if r.get('cluster')]
                    self.out(f"      co-resident chambers at load: {cres}")
                    self.fileonly('crash-full-resident: ' + ', '.join(
                        f"{r['i']}:{r['nm']}(navOK={r['navOK']})" for r in (rec['resident'] or [])))
            if reason == 'process-terminated':
                self.out("VERDICT: the ENTER-with-no-LEAVE chamber above is the load that crashed "
                         "(dossier sec 7.2). Feed it + the co-resident set into CAVE_ENTRY_CHAIN_TRACE.md.")
        else:
            self.out(f"SESSION DETACHED (reason={reason}). No navmesh load was mid-flight "
                     "(all ENTERs had a matching LEAVE).")
            if reason == 'process-terminated':
                self.out("The crash was NOT inside a ProcessRLTD navmesh load at that instant. "
                         "Re-run with --tier full to capture per-tile alloc/memcpy sizes, and note "
                         "the last few LEVEL loads above.")
        self.out('=' * 78)


def main():
    ap = argparse.ArgumentParser(description="Attach the RLTD navmesh crash probe to a RUNNING TQ.exe (read-only).")
    ap.add_argument('--tier', choices=list(TIERS), default='chambers',
                    help="how much to capture (DEFAULT: chambers = SAFEST: only ProcessRLTD enter/leave, "
                         "no hot-path hooks). 'allocs'/'full' add per-tile alloc/memcpy hooks that fire on "
                         "hot paths and add real overhead in the 32-bit target - opt in only when the "
                         "chamber identity alone is not enough.")
    ap.add_argument('--map', default=None, help="override deployed Levels.arc (else auto-discover, DEV preferred).")
    ap.add_argument('--process', default='TQ.exe', help="target process name (default TQ.exe).")
    ap.add_argument('--wait-min', type=float, default=60.0, help="minutes to poll for the process (default 60).")
    ap.add_argument('--gate', action='store_true',
                    help="ALSO hook the mid-function nav gate (Engine+0x1b4158). OFF BY DEFAULT: it is the "
                         "riskiest hook (mid-function trampoline in a hot streaming path) and its 'load=?' "
                         "guid field proved to be a transient value, not chamber identity. ProcessRLTD "
                         "enter/leave alone identifies the crashing chamber.")
    ap.add_argument('--self-test', action='store_true',
                    help="validate map parse + render the agent JS and EXIT. Does NOT attach to any process.")
    ap.add_argument('--loop', action='store_true',
                    help="after each crash capture, RE-ARM automatically and wait for the next TQ.exe launch "
                         "(a fresh timestamped log per crash). Ctrl+C stops. Lets Will keep relaunching/playing "
                         "and every crash is captured without re-running this script.")
    args = ap.parse_args()

    cfg = dict(TIERS[args.tier])
    cfg['gate'] = bool(args.gate)
    map_path = discover_map(args.map)
    print(f"deployed map: {map_path}", flush=True)
    print("parsing LEVELS section (index/GUID -> chamber name) ...", flush=True)
    names, guid2name, cluster = build_name_maps(map_path)
    print(f"  {len(names)} levels; {len(cluster)} blood-cave-cluster chambers", flush=True)
    full_js = render_script(names, guid2name, cluster, cfg)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.self_test:
        rendered = OUT_DIR / 'rendered_selftest.js'
        rendered.write_text(full_js, encoding='utf-8')
        print(f"\n[SELF-TEST] tier={args.tier} cfg={cfg}")
        print(f"[SELF-TEST] rendered agent written: {rendered}  ({len(full_js)} bytes)")
        print(f"[SELF-TEST] cluster sample: {cluster[:8]}{' ...' if len(cluster) > 8 else ''}")
        print("[SELF-TEST] did NOT attach to any process (as designed). OK.")
        return 0

    import frida  # imported here so --self-test works even if frida were absent

    acquire_single_instance_lock()   # never let two probes hook the same TQ.exe

    def run_session():
        """Attach to one TQ.exe lifetime and capture until it crashes/exits.
        Returns 'captured' (process-terminated crash), 'detached' (other reason),
        'timeout' (no TQ.exe in the window), or 'interrupt' (Ctrl+C)."""
        logname = OUT_DIR / f"probe_{datetime.now():%Y%m%d_%H%M%S}.log"
        logf = open(logname, 'w', encoding='utf-8')
        probe = Probe(logf)
        probe.out(f"crash probe starting. tier={args.tier} cfg={cfg}")
        probe.out(f"deployed map: {map_path}")
        probe.out(f"log file: {logname}")
        probe.out(f"frida {frida.__version__}. target='{args.process}'. ATTACH ONLY - the game is never killed.")

        # Poll for an already-running TQ.exe. We only ATTACH; we never spawn it.
        probe.out(f"Waiting for {args.process} - launch the game normally via Steam "
                  f"(polling up to {args.wait_min:.0f} min) ...")
        session = None
        deadline = time.time() + args.wait_min * 60
        i = 0
        while time.time() < deadline:
            try:
                session = frida.attach(args.process)
                break
            except Exception:
                if i % 15 == 0:
                    probe.out(f"  ... still waiting for {args.process} (launch it via Steam) ...")
                i += 1
                time.sleep(2)
        if session is None:
            probe.out(f"{args.process} never appeared within {args.wait_min:.0f} min; stopping.")
            logf.close()
            return 'timeout'
        probe.out(f"ATTACHED - play to the crash area now.")

        def on_detached(reason, *rest):
            probe.detached = reason or 'unknown'

        session.on('detached', on_detached)
        script = session.create_script(full_js)
        script.on('message', probe.on_message)
        script.load()
        probe.out(">>> agent loaded. In-game: progress DEEPER into the blood cave (successive chambers) "
                  "until it crashes or ~15 min. Ctrl+C here detaches (game keeps running).")

        try:
            while probe.detached is None:
                time.sleep(0.5)
            # session detached (very likely a crash). Let any final buffered agent messages
            # (the crashing ENTER, last allocs) drain before summarising the suspect.
            time.sleep(0.4)
            probe.crash_summary(probe.detached)
            if probe.detached == 'process-terminated':
                probe.out('')
                probe.out('*** CRASH CAPTURED ***')
                probe.out('--- last 15 log lines -------------------------------------------------')
                for ln in probe.tail_lines(15):
                    print(ln, flush=True)
                probe.out('---------------------------------------------------------------------')
                probe.out(f"FULL LOG: {logname}")
                probe.out("Send me (Claude) that FULL LOG path and I will pin the crashing chamber.")
                logf.close()
                print(f"log saved: {logname}")
                return 'captured'
            logf.close()
            print(f"log saved: {logname}")
            return 'detached'
        except KeyboardInterrupt:
            probe.out("Ctrl+C - detaching (the game keeps running).")
            if probe.open:
                probe.out(f"note: {len(probe.open)} navmesh load(s) were still in-flight when you stopped: "
                          + ', '.join(f"#{s}:{probe.open[s]['lvl']}" for s in sorted(probe.open)))
            for fn in (getattr(script, 'unload', lambda: None), getattr(session, 'detach', lambda: None)):
                try:
                    fn()
                except Exception:
                    pass
            logf.close()
            return 'interrupt'

    if not args.loop:
        r = run_session()
        return 2 if r == 'timeout' else 0

    # --loop: re-arm automatically after each capture so Will can relaunch/play
    # repeatedly and every crash is captured (a fresh log per crash). Ctrl+C stops.
    print("[LOOP MODE] After each crash the probe RE-ARMS automatically. "
          "Relaunch TQ as many times as you like; Ctrl+C here to stop.", flush=True)
    n = 0
    try:
        while True:
            r = run_session()
            if r == 'interrupt':
                break
            if r == 'timeout':
                print("[LOOP MODE] no TQ.exe within the wait window; stopping.", flush=True)
                break
            n += 1
            print(f"[LOOP MODE] capture #{n} saved. RE-ARMED - relaunch TQ whenever ready "
                  "(Ctrl+C here to stop).", flush=True)
    except KeyboardInterrupt:
        print("[LOOP MODE] stopped.", flush=True)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    finally:
        release_single_instance_lock()
