# Steam Workshop Release — procedure for Will to run

> The exact steps to publish Soulvizier Classic to the Steam Workshop. **This is a
> procedure for Will to run himself** — it needs Will's Steam login + Steam Guard,
> and (for a PUBLIC listing) the upstream-permission legal gate must be cleared
> first. **Do not run the upload as part of automated work.** Last updated: 2026-07-07
> (round-2: corrected the visibility instructions to match `upload_workshop.ps1`'s
> `-Visibility` param, and flagged the confirmed stale-`Text.arc` tag gap).

See also: `SHARE_AND_PLAY.md` (the no-Steam interim path — use this to play with a
friend today) and `MULTIPLAYER_COMPAT.md` (MP fix + determinism).

---

## Before you upload — hard gates

1. **⚖️ LEGAL (required before any PUBLIC listing).** The mod bundles three
   upstream works wholesale:
   - **amgoz1** — Soulvizier 0.98i (on Munderbunny's Underlord)
   - **soa** — Soulvizier AERA (SVAERA)
   - **Dragonlord** — DRX (Diablo Re-eXtinction) visual overhaul
   You need **written permission from all three** before listing this publicly on
   the Workshop. Keeping DRX (Will's decision, 2026-07-04 — no Lite build) keeps
   Dragonlord's permission on the critical path. Credit all three in the Workshop
   description regardless.
   - **Interim while permissions are pending:** upload as **friends-only or
     unlisted** (see visibility below). That lets Will + the friend use Steam's
     auto-download/auto-update without a public listing. A friends-only item is
     not "distribution to the public," but it is still Valve-hosted — if you want
     zero third-party hosting until permissions clear, use the manual zip in
     `SHARE_AND_PLAY.md` instead.

2. **🗺️ Map fix must be stock-engine.** DONE — the navmesh fix is offline-generated
   and Steam-clean (no Engine.dll patch). Never ship a patched DLL via the Workshop
   (a Workshop item is content-only, and Steam "Verify integrity" reverts base-game
   DLLs anyway).

3. **🧷 4GB LAA is instructions, not a shipped file.** The Workshop item cannot ship
   a patched `TQ.exe`. The Workshop description must tell subscribers to apply the
   NTCore 4GB Patch themselves (same as `SHARE_AND_PLAY.md` Step 2).

4. **🌐 MP spawn fix is in the build.** DONE — the deployed `.arz` already contains
   the `/`-free multiplayer spawn-scaling fix (`MULTIPLAYER_COMPAT.md`). Make sure
   you package the *current* built mod, not a stale one. One cheap pre-ship check:
   launch once and confirm the game log has no `RunEquation load failure` on a
   spawn equation (`MULTIPLAYER_COMPAT.md` §M1.5); if it ever does, rebuild with
   `SVC_MP_SPAWN_LINEAR=1` and re-package.

---

## Payload size confirmation

Current packaged payload: **~1.12 GB** (1143 MB uncompressed across the `.arz` +
`.arc` set; the biggest single file is `Levels.arc` at ~685 MB). The Steam
Workshop can host this — SVAERA (the AERA port) is ~1.86 GB live on the same
appid (475150). No size blocker.

---

## Pre-flight checklist

- [ ] Legal: permissions from amgoz1, soa, Dragonlord obtained (for PUBLIC) — or you are intentionally uploading friends-only/unlisted as interim
- [ ] Mod is freshly built and deployed (`bootstrap_working_mod.ps1`; MP fix + latest map present in `work\SoulvizierClassic\`)
- [ ] **`Text.arc` is current — CONFIRMED STALE as of this writing.** The deployed `Text.arc` is missing **8 Blood Toxeus / Crimson Verdict name/desc tags that shipped records actually reference** (`tagMonsterHemorrheus`, `tagSVCSetCrimsonVerdict`, `tagSVCSoulHemorrhage`(+DESC), and the 4 Crimson Verdict item tags + Vein Render); `validate_tags` reports `RESULT: FAIL` (its 171-tag count is a wishlist-superset cross-check — the *referenced-mod gate* passes, and only these 8 render as raw strings in-game; full breakdown in `MULTIPLAYER_COMPAT.md` §M3.1). In-game this shows raw tag strings instead of Hemorrheus's name, the Crimson Verdict set + its 4 pieces, the Vein Render sword, and the Hemorrhage soul. **Rebuild + redeploy `Text.arc` before a public listing** (it is not an MP/determinism/crash problem, so friends-only interim play is unaffected, but it is a visible content bug).
- [ ] SteamCMD present at `C:\steamcmd\steamcmd.exe` (config key `STEAMCMD_EXE`)
- [ ] Will is logged into Steam and has Steam Guard available (phone/email)
- [ ] Visibility decided: the script **defaults to friends-only (`-Visibility 1`)**; use `-Update -Visibility 0` to go public *after* permissions clear (Step 2)
- [ ] Workshop description drafted (credits all three upstreams; links the NTCore 4GB Patch; says "Play via Custom Quest → SoulvizierClassic")

---

## Step 1 — Package the Workshop item (safe, no upload)

```powershell
# from C:\Users\willi\repos\tqit_soulvizier_classic
powershell -ExecutionPolicy Bypass -File scripts\package_workshop.ps1
```

This stages a clean `dist\workshop\SoulvizierClassic\` with `database\`,
`resources\` (all `.arc` files + XPack stubs), and `maps\`. It prints the file
count and total MB. **This does not upload anything.**

> Sanity check after packaging: confirm `dist\workshop\SoulvizierClassic\database\SoulvizierClassic.arz`
> is the current build (its SHA-256 should match the deployed
> `CustomMaps\SoulvizierClassic\Database\SoulvizierClassic.arz`).

---

## Step 2 — Visibility (the script already defaults to friends-only — no edit needed)

`scripts\upload_workshop.ps1` takes a **`-Visibility` parameter** (validated set
`0/1/2/3`) that **defaults to `1` (friends-only)**. It writes `"visibility"
"$Visibility"` into the Workshop VDF, so the **first upload is friends-only by
default** — you do **not** need to hand-edit the script, and there is no hard-coded
`"visibility" "0"` line to change (that instruction was from an older version of
the script; ignore it).

| `-Visibility` value | Meaning |
|--------------------:|---------|
| `0` | Public (needs the legal permissions) |
| `1` | Friends only — **the default** (interim while permissions pend) |
| `2` | Hidden (only you) |
| `3` | Unlisted (only people with the link) |

- **Interim (permissions pending):** just run Step 3 as-is — you get friends-only.
- **Go public later (after permissions clear):** re-run the update with an explicit
  public flag: `scripts\upload_workshop.ps1 -SteamUser <user> -Update -Visibility 0`.
  A visibility change needs no content re-upload beyond writing the flag (you can
  also flip it in the item's Steam Workshop web page).

---

## Step 3 — Upload with SteamCMD (Will runs this; interactive login)

**First upload (creates a NEW Workshop item — friends-only by default):**
```powershell
# from C:\Users\willi\repos\tqit_soulvizier_classic
powershell -ExecutionPolicy Bypass -File scripts\upload_workshop.ps1 -SteamUser <your_steam_username>
```
- No `-Visibility` needed: it defaults to `1` (friends-only), the safe interim while
  permissions pend. (Pass `-Visibility 2` for hidden or `-Visibility 3` for unlisted
  if you prefer.)
- SteamCMD will prompt for Will's **Steam password** and a **Steam Guard code**.
- On success it prints the new Workshop item ID and saves it to
  `local\workshop_item_id.txt`. **Keep that file** — it is how future updates target
  the same item.
- After the first upload, open the item's Steam Workshop page and confirm the
  visibility, title, description, and (recommended) add a preview image + tags.

**Subsequent updates (same item):**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\upload_workshop.ps1 -SteamUser <your_steam_username> -Update
```
(reads the saved item ID from `local\workshop_item_id.txt`; keeps `-Visibility 1`
unless you pass another value).

**Flip to public (only after the legal permissions clear):**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\upload_workshop.ps1 -SteamUser <your_steam_username> -Update -Visibility 0
```

> The upload script is the only step that publishes. It is intentionally left for
> Will to run — it needs his credentials and, for public, the legal gate. Automated
> tooling should package (Step 1) but never invoke Step 3.

---

## Step 4 — Friend subscribes

Once the item is uploaded (friends-only or public):
1. The friend opens the Workshop item page (from the friends-only list, or the
   unlisted link Will sends) and clicks **Subscribe**.
2. Steam auto-downloads the mod into the friend's TQAE. Subsequent updates Will
   uploads auto-download too — this is the main advantage over the manual zip.
3. The friend still applies the **4GB LAA patch** to their own `TQ.exe` (Workshop
   can't ship it) and plays via **Custom Quest → SoulvizierClassic** with a fresh
   dedicated Custom-Quest character.
4. For multiplayer, host/join exactly as in `SHARE_AND_PLAY.md` Step 4.

---

## Notes / gotchas

- **Never run the upload to completion during automated/agent work.** It publishes
  and needs Will's Steam auth; the legal gate is unresolved for public.
- **Dual distribution recommended:** Workshop (auto-update, Steam users) **plus** a
  ModDB/Nexus zip (for GOG/non-Steam players who install via CustomMaps). The
  `SHARE_AND_PLAY.md` zip is exactly the ModDB/Nexus-style artifact.
- **Determinism still applies on Steam:** the Workshop item's files are the same for
  every subscriber, so byte-identity across players is automatic as long as everyone
  is subscribed to the same item version. If Will uploads an update, both players
  re-download it before the next MP session.
- **appid is 475150** (Titan Quest Anniversary Edition) — already set in both scripts.
