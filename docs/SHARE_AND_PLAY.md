# Share & Play - Soulvizier Classic co-op, right now (no Steam needed)

> The simplest path for **Will + a friend to play Soulvizier Classic together
> today**, without waiting on the Steam Workshop. This uses the manual
> "CustomMaps" install that TQAE already supports. Last updated: 2026-07-07.

See also: `MULTIPLAYER_COMPAT.md` (why byte-identical files matter, the MP spawn
fix) and `STEAM_RELEASE.md` (the eventual Workshop path).

---

## The one rule that makes MP work

**Both players must have byte-identical mod files.** TQAE runs multiplayer in
lockstep; if Will's mod and the friend's mod differ by even one byte, the game
will desync or crash. The whole procedure below is built around that rule:
**Will builds/deploys once, shares one zip, the friend extracts that exact zip.**
Do not have the friend build the mod themselves.

---

## Step 1 - Will: build the shareable zip

From the repo (`C:\Users\willi\repos\tqit_soulvizier_classic`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package_custommaps_zip.ps1
```

This produces **`dist\SoulvizierClassic_CustomMaps.zip`** (~1.12 GB - the `.arc`
files are already compressed, so the zip barely shrinks; the staged tree is
1143 MB uncompressed across 53 files). Its top-level folder is
`SoulvizierClassic`, so the friend can extract it straight into their CustomMaps
folder. The script prints the zip's SHA-256 and the embedded `SoulvizierClassic.arz`
SHA-256 - **send those hashes to the friend** so byte-identity can be verified.

### Exact contents of the zip

The zip contains one top-level `SoulvizierClassic\` folder with:

```
SoulvizierClassic\
  Database\
    SoulvizierClassic.arz          ~52 MB   (items, skills, monsters, souls, MP spawn fix)
  Resources\
    Levels.arc                     ~685 MB  (the world + navmeshes - the big one)
    drx.arc, DRXtextures.arc, DRXsounds.arc, DRXeffects.arc   (DRX visual overhaul)
    SVMesh.arc, SVTextures.arc, SVSounds.arc, SVItems.arc, SVEffects.arc  (Soulvizier assets)
    Items.arc, Itemus_Textures.arc, DiabloTextures.arc, HexTextures.arc, LTex.arc, LSounds.arc
    Quests.arc                     (SV area questlines)
    Text.arc                       (names/descriptions)
    XPack2\, XPack3\, XPack4\       (DLC-compat stubs)
```

(The zip is exactly **53 files** under `SoulvizierClassic\Database\` + `SoulvizierClassic\Resources\`. The staged `work\SoulvizierClassic\Maps\` folder is empty, so nothing from it is packaged - the mod's world data lives entirely inside `Resources\Levels.arc`.)

The packaging script deliberately **excludes** dev cruft that must not ship and
that would break byte-identity if only one player had it: `*.md` notes,
`Quests.arc.roundtrip`, `Quests.arc.working_backup`, the `*_report`/`soul_*`
text files, and the `mod_authored_tags.txt` build manifest.

> If you'd rather zip the already-deployed copy instead of `work\`, run the same
> script with `-Source deployed`. Both should be byte-identical for the `.arz`
> after a deploy.

---

## Step 2 - Both players: apply the 4GB LAA patch (required for stability)

Soulvizier Classic is a large mod on a 32-bit engine; without the Large Address
Aware (4GB) patch, TQAE can run out of address space and crash under load. **Both
Will and the friend must patch their own `TQ.exe`** (it is a per-machine change to
the game executable and is not - and cannot be - shipped inside the mod).

1. Download the **NTCore 4GB Patch** (`4gb_patch.exe`) - the standard community tool.
2. Run it and point it at the game executable:
   `...\steamapps\common\Titan Quest Anniversary Edition\TQ.exe`
   (the tool makes a `TQ.exe.Backup` automatically).
3. That's it - the exe is now Large-Address-Aware.

Notes:
- Steam's "Verify integrity of game files" will revert this patch; just re-run the
  4GB patch afterward.
- This does **not** affect byte-identity of the *mod* files (it patches the game
  exe, which both players already have from Steam).
- Will's `TQ.exe` was already LAA-patched locally on 2026-07-04 (backups beside the
  exe). The friend still needs to do it on their machine.

---

## Step 3 - The friend: install the mod

1. Fully close TQAE.
2. Locate the friend's TQ documents folder. It is one of:
   - `Documents\My Games\Titan Quest - Immortal Throne\`
   - `OneDrive\Documents\My Games\Titan Quest - Immortal Throne\` (if OneDrive
     redirects Documents - this is how Will's machine is set up)
3. If a `CustomMaps` folder doesn't exist there yet, create it.
4. Extract `SoulvizierClassic_CustomMaps.zip` so the result is exactly:
   ```
   ...\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Database\SoulvizierClassic.arz
   ...\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc
   ...  (etc.)
   ```
   (i.e. there should be a `CustomMaps\SoulvizierClassic\` folder, **not**
   `CustomMaps\SoulvizierClassic\SoulvizierClassic\`.)
5. **Verify byte-identity:** in PowerShell, run
   `Get-FileHash "...\CustomMaps\SoulvizierClassic\Database\SoulvizierClassic.arz" -Algorithm SHA256`
   and confirm it matches the `.arz` hash Will sent. (Optionally hash `Levels.arc`
   too.) If the hashes match, the two installs are compatible.

---

## Step 4 - Host and join an MP Custom Quest game

Titan Quest MP uses **LAN or direct-IP** hosting (the classic TQ multiplayer
model). One player hosts, the other joins.

**Host (either player):**
1. Launch TQAE (LAA-patched).
2. Main menu → **Multiplayer** → **Host Game**.
3. Choose **Custom Quest / Custom Game** and select **SoulvizierClassic** as the map/quest.
4. **Create a NEW, dedicated Custom-Quest character** for this mod. Never load a
   normal-campaign character into the mod, and never "bounce" a character between
   the mod and the base game - it corrupts the character. (This applies to both
   players.)
5. Set difficulty and start hosting. Note the host's LAN IP if joining by direct IP.

**Joiner (the other player):**
1. Launch TQAE (LAA-patched, same mod installed).
2. Main menu → **Multiplayer** → **Join Game**.
3. Pick the host's game from the LAN list, or enter the host's IP directly.
4. **Create/select a dedicated Custom-Quest character** (again, a fresh one made
   for the mod).
5. Join. If the game immediately desyncs or drops you, the mod files differ -
   go back to Step 3 and re-verify the hashes match.

> Direct-IP over the internet needs the host to be reachable (port-forward the
> TQ port on the host's router, or use a LAN-emulation tool like Radmin VPN /
> Hamachi so both machines appear on the same LAN). LAN or VPN is the least
> fiddly.

---

## The byte-identical-files caveat (read this)

- If the two installs differ, expect **immediate desync or a crash on join**, not
  a graceful error. Verifying the `.arz` (and ideally `Levels.arc`) SHA-256 on
  both machines before playing avoids wasted time.
- **Re-sync on every update.** Any time Will rebuilds the mod (new arz, new map,
  new content), he must send the friend the new zip and both must reinstall -
  otherwise the next session desyncs. The build is deterministic, so an unchanged
  source produces an unchanged hash; a changed hash means "resend the zip."
- Both players also need the **same base-game version** (both on current TQAE via
  Steam). The mod overlays the base game's database, so a base-game mismatch is
  its own desync source.
- The multiplayer spawn-scaling fix (see `MULTIPLAYER_COMPAT.md`) is already baked
  into the shared `.arz`, so both players get correctly-scaled co-op monster
  density automatically - nothing extra to configure.

---

## Quick checklist

- [ ] Will: `package_custommaps_zip.ps1` → `dist\SoulvizierClassic_CustomMaps.zip` built
- [ ] Will: sent the friend the zip **and** the `.arz` SHA-256
- [ ] Both: NTCore 4GB patch applied to their own `TQ.exe`
- [ ] Friend: extracted to `...\CustomMaps\SoulvizierClassic\` (not double-nested)
- [ ] Friend: `.arz` SHA-256 matches Will's
- [ ] Both: created fresh dedicated Custom-Quest characters
- [ ] Host → Multiplayer → Host → Custom Quest → SoulvizierClassic; Joiner joins by LAN/IP
