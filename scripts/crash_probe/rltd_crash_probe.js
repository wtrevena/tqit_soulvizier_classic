'use strict';
// =====================================================================================
// rltd_crash_probe.js  -  Frida agent for the blood-cave heap-corruption crash
// (P0-C, dossier: docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md section 7.2).
//
// READ-ONLY. Every hook only OBSERVES + logs. Nothing is written into the target,
// no memory is patched, no allocation is freed. The runner attaches to an ALREADY
// RUNNING TQ.exe and detaches cleanly; it never spawns or kills the game.
//
// WHAT IT PROVES
//   The recurring crash is heap corruption that detonates inside the engine's
//   navmesh-load path: ProcessRLTD (the REC\x02 / Recast dtTileCache parser),
//   called from the LVL 0x0b nav-load gate, while streaming a deeper blood-cave
//   chamber. The decisive datum is the chamber whose navmesh load logs ENTER with
//   NO matching LEAVE at the crash = the corrupting load (dossier sec 7.2 step 3).
//
// ------------------------------------------------------------------------------------
// RVA ARITHMETIC  (Engine.dll is a 32-bit PE32, preferred ImageBase 0x10000000).
//   With ASLR the module can load at a different base, so we resolve the RUNTIME
//   base at attach and add the RVA. Never use an absolute VA.
//       runtime_VA = engine_base + RVA          RVA = documented_VA - 0x10000000
//   All VAs below are from the dossier appendix ("Appendix: key VAs"):
//     GATE       call ProcessRLTD, LVL 0x0b nav-load gate  0x101b4158 -> RVA 0x1b4158
//     PROCRLTD   ProcessRLTD (REC\x02 parser) entry        0x101f4ba0 -> RVA 0x1f4ba0
//     MEMCPY     per-tile memcpy                           0x100fbb7a -> RVA 0x0fbb7a
//     ALLOC_SLOT per-tile alloc fn-ptr slot (deref @rt)    0x1036f01c -> RVA 0x36f01c
//     REGIONMGR  region-manager global                     0x103743f0 -> RVA 0x3743f0
// ------------------------------------------------------------------------------------
// The runner (run_crash_probe.py) PREPENDS a header that defines PROBE_NAMES /
// PROBE_GUIDMAP / PROBE_CLUSTER / PROBE_CFG from the deployed map. This file is
// valid standalone JavaScript (passes `node --check`); the injected globals are
// resolved at runtime inside the Frida agent.
// =====================================================================================

const RVA = {
  GATE:       0x1b4158,
  PROCRLTD:   0x1f4ba0,
  MEMCPY:     0x0fbb7a,
  ALLOC_SLOT: 0x36f01c,
  REGIONMGR:  0x3743f0,
};

const NAMES   = (typeof PROBE_NAMES   !== 'undefined') ? PROBE_NAMES   : [];   // index -> chamber base name (LEVELS order == level index)
const GUIDMAP = (typeof PROBE_GUIDMAP !== 'undefined') ? PROBE_GUIDMAP : {};   // guid-hex(32) -> chamber base name
const CLUSTER = (typeof PROBE_CLUSTER !== 'undefined') ? PROBE_CLUSTER : [];   // blood-cave cluster base names (loud-flag list)
const CFG     = (typeof PROBE_CFG     !== 'undefined') ? PROBE_CFG     : { alloc: true, memcpy: false, gate: true };

// ---- resolve Engine.dll base (robust across frida versions) --------------------------
function engineModule() {
  try { if (typeof Process.getModuleByName === 'function') return Process.getModuleByName('Engine.dll'); } catch (e) {}
  try { if (typeof Process.findModuleByName === 'function') { const m = Process.findModuleByName('Engine.dll'); if (m) return m; } } catch (e) {}
  const mods = Process.enumerateModules();
  for (const m of mods) { if (m.name.toLowerCase() === 'engine.dll') return m; }
  throw new Error('Engine.dll not found in target process');
}
const mod  = engineModule();
const base = mod.base;
const GATE       = base.add(RVA.GATE);
const PROCRLTD   = base.add(RVA.PROCRLTD);
const MEMCPY     = base.add(RVA.MEMCPY);
const ALLOC_SLOT = base.add(RVA.ALLOC_SLOT);
const REGIONMGR  = base.add(RVA.REGIONMGR);

// ---- low-level readers (proven in tools/debug/frida_probe.py) ------------------------
function hx(ptr, n) {
  try { const b = new Uint8Array(ptr.readByteArray(n)); let s = '';
    for (let i = 0; i < n; i++) s += ('0' + b[i].toString(16)).slice(-2); return s; } catch (e) { return null; }
}
function rd(p)  { try { return p.readPointer(); } catch (e) { return null; } }
function ru8(p) { try { return p.readU8(); } catch (e) { return -1; } }
function isCluster(nm) { return CLUSTER.indexOf(nm) >= 0; }
function nameForGuid(g) { return (g && GUIDMAP[g]) || ('?' + (g ? g.slice(0, 8) : '??')); }

// REC\x02 container detection + register-scan discovery (proven in frida_probe.py).
function isREC(ptr) {
  try { const b = new Uint8Array(ptr.readByteArray(4));
    return b[0] === 0x52 && b[1] === 0x45 && b[2] === 0x43 && b[3] === 0x02; } catch (e) { return false; }
}
function findREC(ctx, args) {
  const cands = [ctx.ecx, ctx.edx, ctx.esi, ctx.eax];
  for (let i = 0; i < 10; i++) { try { cands.push(args[i]); } catch (e) {} }
  for (const c of cands) {
    if (!c) continue;
    try { if (!c.isNull() && isREC(c)) return c; } catch (e) {}
    try { const p = c.readPointer(); if (!p.isNull() && isREC(p)) return p; } catch (e) {}
  }
  return null;
}

// ---- co-residency snapshot (dossier sec 7.2, tests H1) -------------------------------
// [[Engine+0x3743f0]+0x34]+0x50 .. +0x54] = vector<Region*> indexed by level index.
// Per proven frida_sweep.py: region+0x14=ownGUID, region+0x50=Level*, Level+0x6a48=navmeshOK.
// A region is stream-RESIDENT iff [region+0x50] (its Level*) is non-null.
function coResident() {
  const out = [];
  try {
    const P = rd(REGIONMGR); if (!P || P.isNull()) return out;
    const mgr = rd(P.add(0x34)); if (!mgr || mgr.isNull()) return out;
    const beg = rd(mgr.add(0x50)), end = rd(mgr.add(0x54));
    if (!beg || !end || beg.isNull()) return out;
    const nn = end.sub(beg).toInt32() >> 2;
    for (let i = 0; i < nn && i < NAMES.length; i++) {
      const r = rd(beg.add(i * 4)); if (!r || r.isNull()) continue;
      const lvl = rd(r.add(0x50)); if (!lvl || lvl.isNull()) continue;   // not resident
      let nm = NAMES[i];
      const og = hx(r.add(0x14), 16);
      if (og && GUIDMAP[og] && GUIDMAP[og] !== nm) nm = nm + '!=' + GUIDMAP[og];   // index/GUID disagree
      out.push({ i: i, nm: nm, navOK: ru8(lvl.add(0x6a48)), cluster: isCluster(NAMES[i]) });
    }
  } catch (e) {}
  return out;
}

// ---- per-thread ProcessRLTD depth: alloc/memcpy only LOG while a nav parse is on
//      the SAME thread (so the size logs belong to the tile loop, not the whole game) --
const inRLTD = {};   // threadId -> nesting depth
const curSeq = {};   // threadId -> current load seq (for size attribution)
function activeRLTD(tid) { return (inRLTD[tid] || 0) > 0; }

// ---- (4) hot hooks: per-tile alloc size + per-tile memcpy size (dossier sec 7.2) -----
// alloc: `call [Engine+0x36f01c]` -> the slot holds the allocator fn-ptr; deref at attach.
// memcpy: Engine+0x0fbb7a. Both fire globally but only SEND while activeRLTD(thread).
// memcpy is the hottest path in the game, so it is opt-in (CFG.memcpy, default off).
function installHotHooks() {
  if (CFG.alloc) {
    try {
      const allocFn = rd(ALLOC_SLOT);
      if (allocFn && !allocFn.isNull()) {
        Interceptor.attach(allocFn, {
          onEnter(args) {
            if (!activeRLTD(this.threadId)) return;
            let sz = null; try { sz = args[0].toUInt32(); } catch (e) {}
            send({ t: 'alloc', seq: curSeq[this.threadId] || 0, size: sz });
          }
        });
        send({ t: 'info', m: 'alloc hook @' + allocFn + ' (slot Engine+0x36f01c)' });
      } else {
        send({ t: 'warn', m: 'alloc slot deref null; per-tile alloc sizes NOT captured (chamber id unaffected)' });
      }
    } catch (e) { send({ t: 'warn', m: 'alloc hook install failed: ' + e }); }
  }
  if (CFG.memcpy) {
    try {
      Interceptor.attach(MEMCPY, {
        onEnter(args) {
          if (!activeRLTD(this.threadId)) return;
          let sz = null; try { sz = args[2].toUInt32(); } catch (e) {}
          send({ t: 'memcpy', seq: curSeq[this.threadId] || 0, size: sz });
        }
      });
      send({ t: 'info', m: 'memcpy hook @' + MEMCPY + ' (Engine+0x0fbb7a)  [hot path; opt-in]' });
    } catch (e) { send({ t: 'warn', m: 'memcpy hook install failed: ' + e }); }
  }
}

let loadSeq = 0;

// ---- (1) GATE: Engine+0x1b4158 `call ProcessRLTD`. edi = the Level being streamed.
//      Mid-function attach -> onEnter ONLY (no return-address to hang a leave on).
//      Logs the chamber identity at the pre-call instant. Toggle with CFG.gate: if it
//      ever destabilises the game, disable it (--no-gate) - ProcessRLTD's own onEnter
//      still reads edi=Level* and identifies the chamber. ---------------------------------
if (CFG.gate) {
  Interceptor.attach(GATE, {
    onEnter(args) {
      const edi = this.context.edi;
      const og = (edi && !edi.isNull()) ? hx(edi.add(0x14), 16) : null;   // dossier: [Level+0x14] ownGUID
      const nm = nameForGuid(og);
      send({ t: 'gate', seq: loadSeq + 1, edi: edi ? edi.toString() : null, guid: og, lvl: nm, cluster: isCluster(nm) });
    }
  });
}

// ---- (2)/(3) ProcessRLTD: Engine+0x1f4ba0. Real function entry -> safe onEnter+onLeave.
//      ENTER with no matching LEAVE at the crash = the corrupting navmesh load.
//      Snapshots the co-resident chambers "at entry" (dossier sec 7.2, tests H1). ---------
Interceptor.attach(PROCRLTD, {
  onEnter(args) {
    const tid = this.threadId;
    inRLTD[tid] = (inRLTD[tid] || 0) + 1;
    const edi = this.context.edi;                 // caller's edi preserved at entry = Level*
    const rec = findREC(this.context, args);      // PROVEN chamber identity (REC own-guid @ rec+16)
    let nm, og, gc = -1; const deps = [];
    if (rec) {
      gc = rec.add(12).readU32();
      og = hx(rec.add(16), 16);
      nm = nameForGuid(og);
      if (gc > 0 && gc < 64) { for (let i = 0; i < gc; i++) deps.push(nameForGuid(hx(rec.add(16 + i * 16), 16))); }
    } else {
      og = (edi && !edi.isNull()) ? hx(edi.add(0x14), 16) : null;   // fallback: [Level+0x14]
      nm = nameForGuid(og);
    }
    let payload = null; try { if (edi && !edi.isNull()) payload = edi.add(8).readPointer().toString(); } catch (e) {}   // dossier: [edi+8]
    this.seq = ++loadSeq; this.nm = nm; this.cluster = isCluster(nm);
    curSeq[tid] = this.seq;
    send({ t: 'enter', seq: this.seq, lvl: nm, guid: og, gc: gc, deps: deps, payload: payload,
           cluster: this.cluster, resident: coResident() });
  },
  onLeave(ret) {
    const tid = this.threadId;
    const d = (inRLTD[tid] || 0) - 1; inRLTD[tid] = d > 0 ? d : 0;
    if (inRLTD[tid] === 0) curSeq[tid] = 0;
    let al = -1; try { al = ret.toInt32() & 0xff; } catch (e) {}
    send({ t: 'leave', seq: this.seq, lvl: this.nm, al: al, ok: (al !== 0), cluster: this.cluster });
  }
});

installHotHooks();

send({
  t: 'ready',
  base: base.toString(), arch: Process.arch, pointerSize: Process.pointerSize,
  gate: GATE.toString(), procrltd: PROCRLTD.toString(),
  levels: NAMES.length, cluster: CLUSTER.length, cfg: CFG
});
