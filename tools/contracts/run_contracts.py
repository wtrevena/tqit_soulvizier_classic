#!/usr/bin/env python3
"""
run_contracts.py - Soulvizier Classic permanent CONTRACT SUITE runner (integration).

The mod repeatedly ships entities that LOOK complete but are non-functional in-game
(souls whose granted skill never procs, summons that spawn naked, names that render as
raw tags, portals that lead nowhere). This runner is the single command that gates a
build against every permanent contract: for each kind of thing the mod edits, a contract
asserts the shipped artifact carries EACH AND EVERY requirement a functioning base-game
example has.

WHAT IT DOES
  - Discovers every sibling module  tools/contracts/contracts_*.py  (souls, summons,
    resources, map, quests, and any future domain).
  - Builds one shared cfg dict and runs each module's mandated  run(cfg) -> list[dict]
    entrypoint. Each module already applies its own  whitelist_<domain>.txt  inside
    run(), so every violation it returns is NON-WHITELISTED.
  - Aggregates all violations, prints a grouped human-readable report, writes a
    consolidated JSON, and exits 1 iff any P0/P1 survives (fail-loud build-gate law).

Each module is run in an ISOLATED SUBPROCESS by default (this runner re-invokes itself in
--worker mode). Isolation matters: the map and resources modules each parse the ~688 MB
world map and the 54 MB arz, so process isolation frees memory between domains and keeps
one module's crash/OOM from losing the other four's results. A crashed module is reported
as a fail-loud synthetic P1 so the gate never passes on a broken checker. Use --in-process
to run everything in this process (debugging).

USAGE
  # gate the LIVE build tree (work/ + local/) - the default:
  py tools/contracts/run_contracts.py

  # gate the frozen build27 baseline copies under the session scratchpad:
  py tools/contracts/run_contracts.py --baseline

  # override individual artifacts (any subset):
  py tools/contracts/run_contracts.py --arz <path> --levels-arc <path> --text-arc <path> ...

  # write the consolidated JSON to a specific path (default: <temp>/svc_contracts/contracts_violations_ALL.json):
  py tools/contracts/run_contracts.py --baseline --out C:/some/where/contracts_violations_ALL.json

  # run only some domains; list the contract inventory and exit:
  py tools/contracts/run_contracts.py --only souls,map
  py tools/contracts/run_contracts.py --list

Set PYTHONIOENCODING=utf-8 (the harness does). Python: the repo's 3.12 interpreter.

EXIT CODES
  0  clean - no non-whitelisted P0/P1 violation (gate PASS).
  1  at least one non-whitelisted P0/P1 violation, OR a module crashed (gate FAIL).
  2  usage / setup error (an artifact is missing, no modules found, bad --only, ...).
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path

# --------------------------------------------------------------------------- #
# Locations
# --------------------------------------------------------------------------- #
HERE = Path(__file__).resolve().parent               # <repo>/tools/contracts
REPO_ROOT = HERE.parents[1]                           # <repo>

# The frozen build27 baseline copies (created by the domain authors this wave).
_BASELINE_DIR = Path(
    r"C:/Users/willi/AppData/Local/Temp/claude/"
    r"C--Users-willi-repos/55f6c1cb-5e9b-466b-a25d-f3fb1a0c56a8/"
    r"scratchpad/contracts_baseline"
)
_DEFAULT_BASE_GAME = Path(
    r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition"
)

CFG_KEYS = ('arz', 'text_arc', 'levels_arc', 'quests_arc',
            'resource_arc_dir', 'base_game_dir', 'upstream_dir')

SEV_RANK = {'P0': 0, 'P1': 1, 'P2': 2}


# --------------------------------------------------------------------------- #
# Module discovery / import
# --------------------------------------------------------------------------- #
def discover_modules():
    """Return [(domain, path)] for every tools/contracts/contracts_*.py, sorted."""
    out = []
    for p in sorted(HERE.glob('contracts_*.py')):
        domain = p.stem[len('contracts_'):]     # contracts_souls.py -> souls
        out.append((domain, p))
    return out


def import_module_from_path(domain, path):
    """Import a contracts_<domain>.py by path under a unique module name."""
    mod_name = 'svc_contract_%s' % domain
    spec = importlib.util.spec_from_file_location(mod_name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def module_is_conformant(mod):
    """A conformant module exposes callable run(cfg) and a CONTRACTS list."""
    problems = []
    if not hasattr(mod, 'run') or not callable(getattr(mod, 'run')):
        problems.append('missing callable run(cfg)')
    contracts = getattr(mod, 'CONTRACTS', None)
    if not isinstance(contracts, (list, tuple)):
        problems.append('missing CONTRACTS list')
    return problems


# --------------------------------------------------------------------------- #
# cfg building
# --------------------------------------------------------------------------- #
def build_cfg(args):
    """Assemble the shared cfg. --baseline switches the frozen copies in; explicit
    per-artifact flags override anything. Returns (cfg, source_label)."""
    if args.baseline:
        base = Path(args.baseline_dir) if args.baseline_dir else _BASELINE_DIR
        cfg = {
            'arz':              str(base / 'SoulvizierClassic.arz'),
            'text_arc':         str(base / 'Text.arc'),
            'levels_arc':       str(base / 'Levels_merged.arc'),
            'quests_arc':       str(base / 'Quests.arc'),
            'resource_arc_dir': str(base / 'Resources'),
            'base_game_dir':    str(_DEFAULT_BASE_GAME),
            'upstream_dir':     str(REPO_ROOT / 'upstream'),
        }
        source = 'BASELINE (frozen build27 @ %s)' % base
    else:
        work = REPO_ROOT / 'work' / 'SoulvizierClassic'
        res = work / 'Resources'
        # local/Levels_merged.arc is the fresh map-build output and is byte-identical
        # to work/.../Resources/Levels.arc once staged; prefer the work copy, fall
        # back to the local build if the staged copy is absent.
        staged_levels = res / 'Levels.arc'
        local_levels = REPO_ROOT / 'local' / 'Levels_merged.arc'
        levels = staged_levels if staged_levels.is_file() else local_levels
        cfg = {
            'arz':              str(work / 'Database' / 'SoulvizierClassic.arz'),
            'text_arc':         str(res / 'Text.arc'),
            'levels_arc':       str(levels),
            'quests_arc':       str(res / 'Quests.arc'),
            'resource_arc_dir': str(res),
            'base_game_dir':    str(_DEFAULT_BASE_GAME),
            'upstream_dir':     str(REPO_ROOT / 'upstream'),
        }
        source = 'LIVE (work/ + local/)'

    overrides = {
        'arz': args.arz, 'text_arc': args.text_arc, 'levels_arc': args.levels_arc,
        'quests_arc': args.quests_arc, 'resource_arc_dir': args.resource_arc_dir,
        'base_game_dir': args.base_game_dir, 'upstream_dir': args.upstream_dir,
    }
    applied = []
    for k, v in overrides.items():
        if v:
            cfg[k] = v
            applied.append(k)
    if applied:
        source += ' + overrides(%s)' % ','.join(sorted(applied))
    if args.cache_dir:
        cfg['cache_dir'] = args.cache_dir
    return cfg, source


def stage_freshness(cfg):
    """Report the STAGE FRESHNESS of the artifacts being gated (BL-b90-DEBT-1).

    The suite gates a set of separately-built artifacts that are only meaningful
    together: the .arz, the Text.arc built from its tags, the staged Levels/Quests
    arcs, and the resource arcs. A staged companion that is OLDER than the .arz means
    the run is measuring a mix of two builds, and its ground truth cannot be trusted -
    exactly the failure the b80 debt note suspected. (The 1252-P1 case turned out to be
    a missing provenance INPUT instead, now gated fail-loud by C-RES-INPUT-1; staleness
    remained a real, un-instrumented risk either way, so it is surfaced here.)

    Informational only - it never changes the exit code. A build-blocking rule would
    need a real coupling model (Levels+Quests ship together, arz+Text ship together,
    and the DRX/SV resource arcs are legitimately frozen months old), and inventing one
    from mtimes would fire constantly on a healthy tree. Returns list of (key, path,
    mtime, delta_vs_arz_seconds, flag)."""
    rows = []
    arz = cfg.get('arz')
    arz_mtime = None
    if arz and Path(arz).is_file():
        arz_mtime = Path(arz).stat().st_mtime
    # Only the artifacts this repo REBUILDS per wave; the third-party resource arcs
    # (drx.arc, SVMesh.arc, ...) are imported once and never restaged, so comparing
    # their mtimes to the arz would be pure noise.
    for key in ('arz', 'text_arc', 'levels_arc', 'quests_arc'):
        v = cfg.get(key)
        if not v or not Path(v).is_file():
            rows.append((key, v, None, None, 'MISSING' if v else 'unset'))
            continue
        m = Path(v).stat().st_mtime
        d = None if arz_mtime is None else (m - arz_mtime)
        flag = ''
        if key != 'arz' and d is not None and d < -_STALE_SECONDS:
            flag = 'OLDER THAN ARZ by %s' % _human_dt(-d)
        rows.append((key, v, m, d, flag))
    return rows


# A staged companion more than this far behind the .arz is worth naming in the report.
# One hour: shorter than any real wave gap, longer than the minutes a single
# build+restage sequence takes.
_STALE_SECONDS = 3600


def _human_dt(seconds):
    seconds = int(abs(seconds))
    if seconds < 3600:
        return '%dm' % (seconds // 60)
    if seconds < 86400:
        return '%.1fh' % (seconds / 3600.0)
    return '%.1fd' % (seconds / 86400.0)


def validate_cfg(cfg):
    """The .arz is mandatory for every domain. Missing companions are the module's
    business (they degrade gracefully), but we surface which inputs are missing."""
    missing_required = []
    if not cfg.get('arz') or not Path(cfg['arz']).is_file():
        missing_required.append('arz=%s' % cfg.get('arz'))
    present = OrderedDict()
    for k in CFG_KEYS:
        v = cfg.get(k)
        if not v:
            present[k] = ('unset', None)
        else:
            p = Path(v)
            if p.is_file():
                present[k] = ('file', p.stat().st_size)
            elif p.is_dir():
                present[k] = ('dir', None)
            else:
                present[k] = ('MISSING', None)
    return missing_required, present


# --------------------------------------------------------------------------- #
# Worker mode: run ONE module's run(cfg), write its result to a JSON file.
# --------------------------------------------------------------------------- #
def worker_main(module_path, cfg_path, result_path):
    """Executed in a child process. Never raises to the OS: always writes a result
    JSON so the parent can distinguish 'clean' from 'crashed'."""
    result = {'module': Path(module_path).stem, 'contracts': [], 'violations': [],
              'seconds': 0.0, 'error': None, 'notes': []}
    t0 = time.time()
    try:
        with open(cfg_path, 'r', encoding='utf-8') as fh:
            cfg = json.load(fh)
        domain = Path(module_path).stem[len('contracts_'):]
        mod = import_module_from_path(domain, Path(module_path))
        result['contracts'] = list(getattr(mod, 'CONTRACTS', []) or [])
        problems = module_is_conformant(mod)
        if problems:
            result['error'] = 'non-conformant module: ' + '; '.join(problems)
        else:
            viols = mod.run(cfg)
            if not isinstance(viols, list):
                raise TypeError('run(cfg) returned %s, expected list' % type(viols).__name__)
            # normalize + validate each violation dict
            norm = []
            for i, v in enumerate(viols):
                if not isinstance(v, dict):
                    raise TypeError('violation %d is %s, expected dict' % (i, type(v).__name__))
                norm.append({
                    'contract': v.get('contract', '?'),
                    'severity': v.get('severity', '?'),
                    'subject':  v.get('subject', ''),
                    'message':  v.get('message', ''),
                    'evidence': v.get('evidence', ''),
                })
            result['violations'] = norm
            # opportunistically capture any notes the module attached to run()
            notes = getattr(mod.run, 'last_notes', None)
            if isinstance(notes, (list, tuple)):
                result['notes'] = [str(n) for n in notes]
    except BaseException as ex:   # noqa: BLE001 - a worker must never escape uncaught
        import traceback
        result['error'] = '%s: %s' % (type(ex).__name__, ex)
        result['traceback'] = traceback.format_exc()
    result['seconds'] = round(time.time() - t0, 2)
    with open(result_path, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, ensure_ascii=False)
    # exit code mirrors the gate contract for this one module
    p0p1 = any(v['severity'] in ('P0', 'P1') for v in result['violations'])
    return 1 if (p0p1 or result['error']) else 0


def run_module_subprocess(domain, path, cfg, tmpdir, timeout):
    """Spawn this script in --worker mode for one module. Returns the result dict."""
    cfg_path = tmpdir / ('cfg_%s.json' % domain)
    result_path = tmpdir / ('result_%s.json' % domain)
    with open(cfg_path, 'w', encoding='utf-8') as fh:
        json.dump(cfg, fh)
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    cmd = [sys.executable, str(Path(__file__).resolve()), '--worker',
           '--module', str(path), '--cfg', str(cfg_path), '--result', str(result_path)]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True,
                              timeout=timeout)
        stderr_tail = (proc.stderr or '')[-1500:]
    except subprocess.TimeoutExpired:
        return {'module': path.stem, 'contracts': _safe_contracts(path),
                'violations': [], 'seconds': round(time.time() - t0, 2),
                'error': 'TIMEOUT after %ss' % timeout, 'notes': [], 'stderr': ''}
    if result_path.is_file():
        try:
            with open(result_path, 'r', encoding='utf-8') as fh:
                res = json.load(fh)
            res['stderr'] = stderr_tail
            if res.get('seconds') in (None, 0.0):
                res['seconds'] = round(time.time() - t0, 2)
            return res
        except Exception as ex:   # noqa: BLE001
            return {'module': path.stem, 'contracts': _safe_contracts(path),
                    'violations': [], 'seconds': round(time.time() - t0, 2),
                    'error': 'unreadable result file: %s' % ex, 'notes': [],
                    'stderr': stderr_tail}
    return {'module': path.stem, 'contracts': _safe_contracts(path),
            'violations': [], 'seconds': round(time.time() - t0, 2),
            'error': 'worker produced no result (exit %s)' % proc.returncode,
            'notes': [], 'stderr': stderr_tail}


def run_module_inprocess(domain, path, cfg):
    """Run a module in this process (debugging / --in-process). Same result shape."""
    result = {'module': path.stem, 'contracts': [], 'violations': [], 'seconds': 0.0,
              'error': None, 'notes': [], 'stderr': ''}
    t0 = time.time()
    try:
        mod = import_module_from_path(domain, path)
        result['contracts'] = list(getattr(mod, 'CONTRACTS', []) or [])
        problems = module_is_conformant(mod)
        if problems:
            result['error'] = 'non-conformant module: ' + '; '.join(problems)
        else:
            viols = mod.run(cfg)
            result['violations'] = [{
                'contract': v.get('contract', '?'), 'severity': v.get('severity', '?'),
                'subject': v.get('subject', ''), 'message': v.get('message', ''),
                'evidence': v.get('evidence', ''),
            } for v in viols]
            notes = getattr(mod.run, 'last_notes', None)
            if isinstance(notes, (list, tuple)):
                result['notes'] = [str(n) for n in notes]
    except BaseException as ex:   # noqa: BLE001
        import traceback
        result['error'] = '%s: %s' % (type(ex).__name__, ex)
        result['traceback'] = traceback.format_exc()
    result['seconds'] = round(time.time() - t0, 2)
    return result


def _safe_contracts(path):
    """Best-effort CONTRACTS read for a module that failed to run (report inventory)."""
    try:
        domain = path.stem[len('contracts_'):]
        mod = import_module_from_path(domain, path)
        return list(getattr(mod, 'CONTRACTS', []) or [])
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def _fmt_counts(viols):
    c = Counter(v['severity'] for v in viols)
    return c.get('P0', 0), c.get('P1', 0), c.get('P2', 0)


def print_report(results, cfg, source, present, out_path, elapsed, show_examples=10):
    """Grouped human-readable report to stdout."""
    line = '=' * 78
    thin = '-' * 78
    p = print
    p(line)
    p(' SOULVIZIER CLASSIC - PERMANENT CONTRACT SUITE')
    p(' source: %s' % source)
    p(line)
    p(' artifacts:')
    for k in CFG_KEYS:
        kind, size = present.get(k, ('?', None))
        val = cfg.get(k) or '(unset)'
        sz = ('  [%s, %s]' % (kind, _human(size))) if size is not None else ('  [%s]' % kind)
        p('   %-17s %s%s' % (k, val, sz))
    p('')

    # STAGE FRESHNESS (informational; BL-b90-DEBT-1). A staged companion older than the
    # .arz means this run is measuring a mix of two builds - the ground truth the whole
    # suite rests on. Never affects the exit code; see stage_freshness().
    rows = stage_freshness(cfg)
    flagged = [r for r in rows if r[4] and r[4] not in ('unset',)]
    p(' stage freshness (vs the .arz; informational, does not gate):')
    for key, path, m, d, flag in rows:
        when = time.strftime('%Y-%m-%d %H:%M', time.localtime(m)) if m else '-'
        rel = '' if d is None else ('same' if abs(d) < 60 else
                                    ('+%s' % _human_dt(d) if d > 0 else '-%s' % _human_dt(d)))
        p('   %-17s %-16s %-8s %s' % (key, when, rel, flag))
    if flagged:
        p('   NOTE: %d artifact(s) flagged above - re-stage (scripts/bootstrap_working_mod.ps1)'
          % len(flagged))
        p('         before trusting this run as ground truth.')
    p('')

    total_contracts = sum(len(r['contracts']) for r in results)
    p(' modules: %d   contracts: %d   wall: %.1fs' %
      (len(results), total_contracts, elapsed))
    p('')
    # per-module one-liners
    for r in sorted(results, key=lambda x: x['module']):
        p0, p1, p2 = _fmt_counts(r['violations'])
        status = 'OK'
        if r.get('error'):
            status = 'CRASH'
        elif p0 + p1:
            status = 'FAIL'
        p('  [%-22s] %2d contracts | %5d viol (%3d P0, %3d P1, %5d P2) | %6.1fs  %s'
          % (r['module'], len(r['contracts']), len(r['violations']), p0, p1, p2,
             r.get('seconds', 0.0), status))
        if r.get('error'):
            p('        ERROR: %s' % r['error'])
            if r.get('stderr'):
                tail = r['stderr'].strip().splitlines()[-3:]
                for t in tail:
                    p('        | %s' % t)
    p('')

    # global violation roll-up, grouped by contract, ordered by severity
    all_viols = []
    for r in results:
        for v in r['violations']:
            v2 = dict(v)
            v2['domain'] = r['module']
            all_viols.append(v2)

    by_contract = OrderedDict()
    for v in all_viols:
        by_contract.setdefault((v['severity'], v['domain'], v['contract']), []).append(v)
    ordered = sorted(by_contract.items(),
                     key=lambda kv: (SEV_RANK.get(kv[0][0], 9), kv[0][1], kv[0][2]))

    if all_viols:
        p(thin)
        p(' VIOLATIONS BY CONTRACT  (non-whitelisted; most-severe first)')
        p(thin)
        for (sev, domain, contract), vs in ordered:
            p(' %-3s %-26s %-9s x%-5d  %s'
              % (sev, contract, domain, len(vs), vs[0].get('message', '')[:60]))
            for v in vs[:show_examples]:
                subj = str(v.get('subject', ''))[:80]
                p('        - %s' % subj)
            if len(vs) > show_examples:
                p('        ... +%d more' % (len(vs) - show_examples))
        p('')

    p0 = sum(1 for v in all_viols if v['severity'] == 'P0')
    p1 = sum(1 for v in all_viols if v['severity'] == 'P1')
    p2 = sum(1 for v in all_viols if v['severity'] == 'P2')
    crashed = [r['module'] for r in results if r.get('error')]
    p(line)
    p(' TOTAL: %d violations  (%d P0, %d P1, %d P2)  across %d modules'
      % (len(all_viols), p0, p1, p2, len(results)))
    if crashed:
        p(' CRASHED MODULES (fail-loud): %s' % ', '.join(crashed))
    gate_fail = bool(p0 + p1) or bool(crashed)
    p(' GATE: %s%s' % ('FAIL' if gate_fail else 'PASS',
                       ('  (%d P0/P1 blocking)' % (p0 + p1)) if (p0 + p1) else ''))
    if out_path:
        p(' consolidated JSON: %s' % out_path)
    p(line)
    return gate_fail


def _human(n):
    if n is None:
        return '?'
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return '%.0f%s' % (n, unit) if unit == 'B' else '%.1f%s' % (n, unit)
        n /= 1024.0


def build_consolidated_json(results, cfg, source):
    """The machine-readable consolidated report."""
    all_viols = []
    per_contract = Counter()
    per_contract_sev = {}
    for r in results:
        for v in r['violations']:
            v2 = dict(v)
            v2['domain'] = r['module']
            all_viols.append(v2)
            per_contract[v['contract']] += 1
            per_contract_sev[v['contract']] = v['severity']
    p0 = sum(1 for v in all_viols if v['severity'] == 'P0')
    p1 = sum(1 for v in all_viols if v['severity'] == 'P1')
    p2 = sum(1 for v in all_viols if v['severity'] == 'P2')
    crashed = [r['module'] for r in results if r.get('error')]

    domains = []
    for r in sorted(results, key=lambda x: x['module']):
        dp0, dp1, dp2 = _fmt_counts(r['violations'])
        cc = Counter(v['contract'] for v in r['violations'])
        domains.append({
            'domain': r['module'],
            'contracts_declared': len(r['contracts']),
            'contract_ids': [c.get('id') for c in r['contracts']],
            'violations': len(r['violations']),
            'p0': dp0, 'p1': dp1, 'p2': dp2,
            'seconds': r.get('seconds'),
            'error': r.get('error'),
            'notes': r.get('notes', []),
            'counts_by_contract': dict(cc),
        })

    return {
        'suite': 'soulvizier_classic_contracts',
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'source': source,
        'cfg': {k: cfg.get(k) for k in CFG_KEYS},
        'totals': {
            'modules': len(results),
            'contracts_declared': sum(len(r['contracts']) for r in results),
            'violations': len(all_viols),
            'p0': p0, 'p1': p1, 'p2': p2,
            'blocking_p0p1': p0 + p1,
            'crashed_modules': crashed,
            'gate': 'FAIL' if (p0 + p1 or crashed) else 'PASS',
        },
        'counts_by_contract': [
            {'contract': cid, 'severity': per_contract_sev.get(cid), 'count': n}
            for cid, n in sorted(per_contract.items(),
                                 key=lambda kv: (SEV_RANK.get(per_contract_sev.get(kv[0]), 9), kv[0]))
        ],
        'domains': domains,
        'violations': all_viols,
    }


# --------------------------------------------------------------------------- #
# --list (inventory only)
# --------------------------------------------------------------------------- #
def print_inventory(modules):
    line = '=' * 78
    print(line)
    print(' SOULVIZIER CLASSIC - CONTRACT INVENTORY')
    print(line)
    total = 0
    for domain, path in modules:
        try:
            mod = import_module_from_path(domain, path)
            contracts = list(getattr(mod, 'CONTRACTS', []) or [])
        except Exception as ex:   # noqa: BLE001
            print(' [%s] FAILED TO IMPORT: %s' % (domain, ex))
            continue
        print('\n [%s]  %d contracts' % (domain, len(contracts)))
        total += len(contracts)
        for c in contracts:
            print('   %-26s %s' % (c.get('id', '?'), c.get('name', '')))
            asserts = (c.get('asserts', '') or '').strip()
            if asserts:
                print('       assert: %s' % _wrap(asserts, 66, 15))
            dfrom = (c.get('derived_from', '') or '').strip()
            if dfrom:
                print('       from:   %s' % _wrap(dfrom, 66, 15))
    print('\n' + line)
    print(' %d modules, %d contracts total' % (len(modules), total))
    print(line)


def _wrap(text, width, indent):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w) if cur else w
    if cur:
        lines.append(cur)
    pad = '\n' + ' ' * indent
    return pad.join(lines)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def parse_args(argv):
    ap = argparse.ArgumentParser(
        prog='run_contracts.py',
        description='Run the Soulvizier Classic permanent contract suite as a build gate.',
        add_help=True)
    ap.add_argument('--baseline', action='store_true',
                    help='gate the frozen build27 baseline copies (default: LIVE work/+local/).')
    ap.add_argument('--baseline-dir', default=None,
                    help='override the baseline directory used by --baseline.')
    for k in CFG_KEYS:
        ap.add_argument('--' + k.replace('_', '-'), default=None,
                        help='override cfg[%s].' % k)
    ap.add_argument('--cache-dir', default=None,
                    help='cfg[cache_dir] for modules that cache (resources).')
    ap.add_argument('--out', default=None,
                    help='consolidated JSON output path (default: <temp>/svc_contracts/contracts_violations_ALL.json).')
    ap.add_argument('--only', default=None,
                    help='comma-separated domain names to run (e.g. souls,map).')
    ap.add_argument('--in-process', action='store_true',
                    help='run modules in this process instead of isolated subprocesses (debug).')
    ap.add_argument('--timeout', type=int, default=600,
                    help='per-module subprocess timeout in seconds (default 600).')
    ap.add_argument('--examples', type=int, default=10,
                    help='max exemplar subjects printed per contract (default 10).')
    ap.add_argument('--list', action='store_true',
                    help='print the contract inventory and exit (no run).')
    # worker-mode (internal)
    ap.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--module', default=None, help=argparse.SUPPRESS)
    ap.add_argument('--cfg', default=None, help=argparse.SUPPRESS)
    ap.add_argument('--result', default=None, help=argparse.SUPPRESS)
    return ap.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    # ---- worker mode: run one module and exit ----
    if args.worker:
        if not (args.module and args.cfg and args.result):
            sys.stderr.write('worker mode requires --module --cfg --result\n')
            return 2
        return worker_main(args.module, args.cfg, args.result)

    modules = discover_modules()
    if not modules:
        sys.stderr.write('ERROR: no contracts_*.py modules found in %s\n' % HERE)
        return 2

    if args.only:
        wanted = {s.strip() for s in args.only.split(',') if s.strip()}
        have = {d for d, _ in modules}
        unknown = wanted - have
        if unknown:
            sys.stderr.write('ERROR: unknown domain(s) %s; available: %s\n'
                             % (', '.join(sorted(unknown)), ', '.join(sorted(have))))
            return 2
        modules = [(d, p) for d, p in modules if d in wanted]

    if args.list:
        print_inventory(modules)
        return 0

    cfg, source = build_cfg(args)
    missing_required, present = validate_cfg(cfg)
    if missing_required:
        sys.stderr.write('ERROR: required artifact missing: %s\n'
                         % '; '.join(missing_required))
        sys.stderr.write('       (use --baseline, or pass --arz / --levels-arc / ... overrides)\n')
        return 2

    # output path
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = Path(os.environ.get('TEMP', '.')) / 'svc_contracts' / 'contracts_violations_ALL.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # temp dir for worker cfg/result files
    tmpdir = Path(os.environ.get('TEMP', '.')) / 'svc_contracts' / 'run'
    tmpdir.mkdir(parents=True, exist_ok=True)

    sys.stderr.write('[run_contracts] %s\n' % source)
    sys.stderr.write('[run_contracts] running %d module(s): %s\n'
                     % (len(modules), ', '.join(d for d, _ in modules)))

    t0 = time.time()
    results = []
    for domain, path in modules:
        sys.stderr.write('   -> %s ...\n' % domain)
        sys.stderr.flush()
        if args.in_process:
            res = run_module_inprocess(domain, path, cfg)
        else:
            res = run_module_subprocess(domain, path, cfg, tmpdir, args.timeout)
        results.append(res)
        p0, p1, p2 = _fmt_counts(res['violations'])
        tag = ('ERROR:%s' % res['error']) if res.get('error') else \
              ('%dP0 %dP1 %dP2' % (p0, p1, p2))
        sys.stderr.write('      done %s (%.1fs) %s\n'
                         % (domain, res.get('seconds', 0.0), tag))
        sys.stderr.flush()
    elapsed = time.time() - t0

    # write consolidated JSON
    consolidated = build_consolidated_json(results, cfg, source)
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(consolidated, fh, ensure_ascii=False, indent=2)

    gate_fail = print_report(results, cfg, source, present, out_path, elapsed,
                             show_examples=args.examples)
    return 1 if gate_fail else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
