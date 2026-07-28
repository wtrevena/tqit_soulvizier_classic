# PERMISSIONS - upstream reuse grants (Soulvizier Classic)

> **Trust level: LIVE - keep this current.** The single durable record of upstream-author
> permission to reuse their work in Soulvizier Classic. The Steam publish gate that consumes
> this record lives in `docs/STEAM_RELEASE.md` (section "Before you upload - hard gates").
> `CLAUDE.md` lists the three upstream authors for credit; this file tracks the PERMISSION state.
> Last updated: 2026-07-10.

Soulvizier Classic bundles three upstream works wholesale (a total conversion). Each author's
reuse permission is tracked below. Public Workshop listing (item 3759792705) requires clearing
the legal gate; credit all three in the Workshop description regardless of permission state.

---

## Grants

| Upstream | Author | Scope reused | Permission | Form | Recorded |
|---|---|---|---|---|---|
| Soulvizier 0.98i (on Munderbunny's Underlord) | **amgoz1** | The classic SV back-port: souls, masteries, legacy skills, questlines, Super Caravan, enchanting design bible | **GRANTED (written)** | Email correspondence - Will emailed amgoz1 directly | 2026-07-27 (relayed by Will) |
| Soulvizier AERA (SVAERA) | **soa** | SVAERA content used as the merge base, plus the additive mastery grafts (graft #0 PC anim-row completion + the additive skill grafts per `docs/SVAERA_MASTERY_COMPARISON.md`) | **GRANTED (verbal)** | Verbal - relayed by Will 2026-07-10 | 2026-07-10 |
| DRX (Diablo Re-eXtinction) visual overhaul | **Dragonlord** | The DRX meshes/textures/visual overhaul kept in the shipped mod (Will's 2026-07-04 "keep DRX" decision keeps this on the critical path) | Standing obligation - not yet captured in writing | - | - |

---

## soa (SVAERA) - detail

- **Grant:** soa gave **verbal permission** to reuse his SVAERA work in this mod.
- **Provenance:** relayed by Will on 2026-07-10. Quote (Will): "he said it was cool."
- **Scope covered:** additive reuse of soa's SVAERA content on top of our tuned trees - specifically
  the mastery-adoption grafts recorded in `docs/SVAERA_MASTERY_COMPARISON.md`: graft #0 (restoring the
  dropped vanilla melee anim clips onto our PC anim tables, byte-identical to base/SVAERA) and the
  additive Atlantis/DRX player-skill grafts (Slam/Fissure/Lasting Legacy, Active Block/Summon Phalanx,
  Fire Nova/Rupture line, Lightning Dash/Frost Nova, Earthbind/Rootwave, Summon Doppelganger, and the
  later Rune Golem follow-up). These are additive reuse squarely within a "reuse his work" grant.
- **Still to do (durable paper trail):** obtain a **written** confirmation (forum PM or Discord message)
  to attach to the release record, because a public Workshop listing benefits from a durable trail.
  Until then this verbal grant is the record of authority. If soa ever objects, the fallback is the same
  as for any upstream: set the item unlisted/hidden (`-Visibility 3`/`2`) or pull it, and use the manual
  zip path in `docs/SHARE_AND_PLAY.md`.

## amgoz1 (SV 0.98i) - GRANTED

- **Grant:** amgoz1 gave **written permission** by email to reuse his Soulvizier work in this mod.
- **Provenance:** Will corresponded with him directly by email; relayed by Will 2026-07-27 ("we already
  have written permission from amgoz1, i was emailing him"). This SUPERSEDES the prior
  "standing obligation - not yet captured in writing" state recorded here through 2026-07-27.
- ⚠️ **ACTION (paper trail, Will only):** the email itself is the durable artifact and is not yet in the
  repo. Save the thread (PDF or .eml export, sender address and date visible) and drop it beside this
  file, or paste the operative sentence here verbatim. Until then this line is a relay, not the document.
- ⚠️ **SCOPE - open question for Will:** it is not recorded whether the grant covers the mod CONTENT
  only, or also amgoz1's ARTWORK (the ModDB "SV" emblem/logo we want as the Steam cover image, harvested
  to `local/artwork_amgoz1/`). Content reuse and promotional-art reuse are separable permissions. If the
  email is general ("use my mod / do what you like with it"), the artwork is reasonably covered; if it is
  specific to the mod files, ask him the one extra question before the emblem goes on the public listing.
- **Credit:** amgoz1 is credited in the Workshop description regardless (he set that norm himself -
  his own ModDB page thanks Munderbunny, Swift and Kirii for allowing him to use their content).

## Dragonlord (DRX)

- **Standing obligation**: get written permission. Keeping DRX (no Lite build, Will 2026-07-04) keeps
  Dragonlord on the critical path. Credit in the Workshop description. Update the table above when
  obtained - the amgoz1 grant above is the template for how to record it.
