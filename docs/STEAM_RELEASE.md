# Steam Workshop Release - procedure for Will to run

> The exact steps to publish Soulvizier Classic to the Steam Workshop. **This is a
> procedure for Will to run himself** - it needs Will's Steam login + Steam Guard,
> and (for a PUBLIC listing) the upstream-permission legal gate must be cleared
> first. **Do not run the upload as part of automated work.** Last updated: 2026-07-07
> (round-2: corrected the visibility instructions to match `upload_workshop.ps1`'s
> `-Visibility` param, and flagged the confirmed stale-`Text.arc` tag gap).

> **⚠️ UPDATE 2026-07-08 - the item is already LIVE and PUBLIC.** Soulvizier Classic is published
> as Steam Workshop item **3759792705**, visibility **public** (`-Visibility 0`). The parts of this
> doc written as if the *first* upload is still pending and defaults to friends-only are **SUPERSEDED**
> - they are kept for history and for the mechanics of the `-Visibility` flag, but the current
> reality is: the item exists, is public, and future changes go out as **updates**
> (`-Update -Visibility 0`). Also the packaging layout changed on 2026-07-08 (commit `1851203`, tag
> `workshop-wrapper-fix`): the staging tree is now `dist\workshop\content\SoulvizierClassic\` (a single
> wrapper), not the old wrapperless `dist\workshop\SoulvizierClassic\`. See Step 1 below and
> `docs/PLAYBOOK.md` §3 / `docs/HANDOFF_LIVE_STATE.md` §3.

See also: `SHARE_AND_PLAY.md` (the no-Steam path - a manual CustomMaps zip for GOG/non-Steam
players or LAN co-op) and `MULTIPLAYER_COMPAT.md` (MP fix + determinism).

---

## Before you upload - hard gates

1. **⚖️ LEGAL (required before any PUBLIC listing).** The mod bundles three
   upstream works wholesale:
   - **amgoz1** - Soulvizier 0.98i (on Munderbunny's Underlord)
   - **soa** - Soulvizier AERA (SVAERA)
   - **Dragonlord** - DRX (Diablo Re-eXtinction) visual overhaul
   You need **written permission from all three** before listing this publicly on
   the Workshop. Keeping DRX (Will's decision, 2026-07-04 - no Lite build) keeps
   Dragonlord's permission on the critical path. Credit all three in the Workshop
   description regardless.
   - **SUPERSEDED (kept for history):** this originally advised uploading friends-only or
     unlisted as an interim while permissions were pending. The item is now PUBLIC, so that
     interim path no longer applies. If an upstream author objects, the fallback is to set the
     item unlisted/hidden (`-Visibility 3`/`2`) or pull it, and use the manual zip in
     `SHARE_AND_PLAY.md` for zero third-party hosting.

2. **🗺️ Map fix must be stock-engine.** DONE - the navmesh fix is offline-generated
   and Steam-clean (no Engine.dll patch). Never ship a patched DLL via the Workshop
   (a Workshop item is content-only, and Steam "Verify integrity" reverts base-game
   DLLs anyway).

3. **🧷 4GB LAA is instructions, not a shipped file.** The Workshop item cannot ship
   a patched `TQ.exe`. The Workshop description must tell subscribers to apply the
   NTCore 4GB Patch themselves (same as `SHARE_AND_PLAY.md` Step 2).

4. **🌐 MP spawn fix is in the build.** DONE - the deployed `.arz` already contains
   the `/`-free multiplayer spawn-scaling fix (`MULTIPLAYER_COMPAT.md`). Make sure
   you package the *current* built mod, not a stale one. One cheap pre-ship check:
   launch once and confirm the game log has no `RunEquation load failure` on a
   spawn equation (`MULTIPLAYER_COMPAT.md` §M1.5); if it ever does, rebuild with
   `SVC_MP_SPAWN_LINEAR=1` and re-package.

---

## Payload size confirmation

Current packaged payload: **~1.12 GB** (1143 MB uncompressed across the `.arz` +
`.arc` set; the biggest single file is `Levels.arc` at ~685 MB). The Steam
Workshop can host this - SVAERA (the AERA port) is ~1.86 GB live on the same
appid (475150). No size blocker.

---

## Pre-flight checklist

- [ ] Legal/credits: the item is already PUBLIC, so the Workshop description must credit amgoz1, soa, Dragonlord; if written permission from any upstream is still outstanding, that is a standing obligation to resolve (be ready to set the item unlisted/hidden if an author objects)
- [ ] Mod is freshly built and deployed (`bootstrap_working_mod.ps1`; MP fix + latest map present in `work\SoulvizierClassic\`)
- [ ] **`Text.arc` is current - CONFIRMED STALE as of this writing.** The deployed `Text.arc` is missing **8 Blood Toxeus / Crimson Verdict name/desc tags that shipped records actually reference** (`tagMonsterHemorrheus`, `tagSVCSetCrimsonVerdict`, `tagSVCSoulHemorrhage`(+DESC), and the 4 Crimson Verdict item tags + Vein Render); `validate_tags` reports `RESULT: FAIL` (its 171-tag count is a wishlist-superset cross-check - the *referenced-mod gate* passes, and only these 8 render as raw strings in-game; full breakdown in `MULTIPLAYER_COMPAT.md` §M3.1). In-game this shows raw tag strings instead of Hemorrheus's name, the Crimson Verdict set + its 4 pieces, the Vein Render sword, and the Hemorrhage soul. **The item is already public, so these raw tags are visible to every subscriber right now** - fix ASAP via a coupled `arz` + `Text.arc` push (tags changed = ship both together). It is not an MP/determinism/crash problem, but it is a visible content bug. Tracked as **`B-TEXT-TAGS-1`** in `docs/BACKLOG.md`.
- [ ] SteamCMD present at `C:\steamcmd\steamcmd.exe` (config key `STEAMCMD_EXE`)
- [ ] Will is logged into Steam and has Steam Guard available (phone/email)
- [ ] Visibility: the item is live at `-Visibility 0` (public); **always pass `-Update -Visibility 0`** on an update (a bare `-Update` writes the script's `-Visibility 1` default and would flip it to friends-only; see Step 2)
- [ ] Workshop description drafted (credits all three upstreams; links the NTCore 4GB Patch; says "Play via Custom Quest → SoulvizierClassic")

---

## Step 1 - Package the Workshop item (safe, no upload)

```powershell
# from C:\Users\willi\repos\tqit_soulvizier_classic
powershell -ExecutionPolicy Bypass -File scripts\package_workshop.ps1
```

This stages the item under **`dist\workshop\content\SoulvizierClassic\`** - a SINGLE wrapper folder
with `database\` (the `.arz`) and `resources\` (all `.arc` files + XPack stubs) inside it. SteamCMD
uploads the CONTENTS of the vdf `contentfolder` (`dist\workshop\content`), whose only child is
`SoulvizierClassic`, so the item root ends up as one `SoulvizierClassic` mod. It prints the packaged
`Levels.arc` size + MD5, the file count and total MB. **This does not upload anything.**

The packager has two fail-loud guards (both added 2026-07-08): it **ABORTS if the packaged
`Levels.arc` is byte-identical to the local-only TESTHUB map** (`local\Levels_merged_TESTHUB.arc`),
and it **asserts the content root holds exactly one folder, `SoulvizierClassic`** (the guard against
the old "two mods database/resources" bug regressing). It also deletes the stale wrapperless
`dist\workshop\SoulvizierClassic\` layout every run.

> Sanity check after packaging: confirm
> `dist\workshop\content\SoulvizierClassic\database\SoulvizierClassic.arz` is the current build - its
> SHA-256 should match the deployed `CustomMaps\SoulvizierClassic\Database\SoulvizierClassic.arz`.
> Current build27 arz: **54,529,030 B, MD5 `7C6E209988F0CE815BAF35F058B6A0A8`, SHA-256
> `5014f1903aa4163adaeb8c35fd71ca8fe36db2a7293aa874932660619b600c8f`** (verified 2026-07-08). The
> packaged Levels.arc must be the canonical map **688,691,849 B, MD5 `A1BA5DB2F00FFA067A808753A2E1EAC5`**
> - NOT the TESTHUB variant (the guard enforces this).

---

## Step 2 - Visibility

> **CURRENT STATE:** item 3759792705 is already published at **`-Visibility 0` (public)**. For any
> future change, pass `-Update -Visibility 0` to keep it public. The friends-only-first-upload framing
> below is **SUPERSEDED** (there is no "first upload" left to do); it is kept only to document what the
> `-Visibility` param does.

`scripts\upload_workshop.ps1` takes a **`-Visibility` parameter** (validated set
`0/1/2/3`) that **defaults to `1` (friends-only)** for a brand-new item. It writes
`"visibility" "$Visibility"` into the Workshop VDF. Since the item already exists and is public, you
always pass `-Update -Visibility 0`; the default only ever mattered for the original first upload.

| `-Visibility` value | Meaning |
|--------------------:|---------|
| `0` | Public - **the current live setting** |
| `1` | Friends only (the script default for a brand-new item) |
| `2` | Hidden (only you) |
| `3` | Unlisted (only people with the link) |

- **Keep it public (normal case):** `scripts\upload_workshop.ps1 -SteamUser <user> -Update -Visibility 0`.
- A visibility change needs no content re-upload beyond writing the flag (you can also flip it on the
  item's Steam Workshop web page).
- **Legal / credits note (still standing):** the mod bundles three upstream works (amgoz1 / soa /
  Dragonlord). The item is public, so make sure the Workshop description credits all three; if written
  permission from any upstream is still outstanding, that remains an open obligation to resolve -
  track it, and be ready to set the item to unlisted/hidden if an author objects.

---

## Step 3 - Upload with SteamCMD (Will runs this; interactive login)

**The normal case now - update the existing PUBLIC item:**
```powershell
# from C:\Users\willi\repos\tqit_soulvizier_classic
powershell -ExecutionPolicy Bypass -File scripts\upload_workshop.ps1 -SteamUser <your_steam_username> -Update -Visibility 0
```
- `-Update` reads the saved item id from `local\workshop_item_id.txt` (currently `3759792705`) and
  pushes a delta to that same item.
- **Always pass `-Visibility 0` on an update.** The script writes `"visibility" "$Visibility"` into
  the VDF every run and the param **defaults to `1` (friends-only)** - so running `-Update` WITHOUT
  `-Visibility 0` would flip the live public item to friends-only. Pass `0` to keep it public.
- SteamCMD will prompt for Will's **Steam password** and a **Steam Guard code** (the session is
  usually cached, so it may not re-prompt).
- After it finishes, open the item's Steam Workshop page and confirm visibility, title, description,
  and (recommended) a preview image + tags.

**History (SUPERSEDED - the item already exists, do not do this):** the original *first* upload was
`upload_workshop.ps1 -SteamUser <user>` (no `-Update`), which created the item and saved its id to
`local\workshop_item_id.txt`. That id is now populated (`3759792705`), so a no-`-Update` run would try
to create a SECOND item and prompt for confirmation. Do not run it; always use `-Update -Visibility 0`.

> The upload script is the only step that publishes. It is intentionally left for
> Will to run - it needs his credentials and, for public, the legal gate. Automated
> tooling should package (Step 1) but never invoke Step 3.

---

## Step 4 - Friend subscribes

The item is public, so anyone can subscribe:
1. The friend opens the public Workshop item page (item 3759792705 - searchable, or Will sends the
   direct link) and clicks **Subscribe**.
2. Steam auto-downloads the mod into the friend's TQAE. Subsequent updates Will
   uploads auto-download too - this is the main advantage over the manual zip.
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
- **appid is 475150** (Titan Quest Anniversary Edition) - already set in both scripts.
