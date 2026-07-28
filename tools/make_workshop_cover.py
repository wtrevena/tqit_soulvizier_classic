#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_workshop_cover.py - build the Steam Workshop cover image for Soulvizier Classic.

Source art: amgoz1's Soulvizier v0.96 patch emblem (the horned shield + glowing "SV"),
harvested to local/artwork_amgoz1/ with provenance in that folder's SOURCES.md.
Reuse is covered by amgoz1's written permission (docs/PERMISSIONS.md, granted by email,
recorded 2026-07-27).

The emblem has the upstream version number "0.96" burned into it, which is wrong for an
AE port. We paint that region out using colour sampled from the emblem's own backdrop and
set our own subtitle in its place, so the mark keeps amgoz1's visual identity while
reading correctly for this mod.

Steam preview constraints: JPG/PNG, < 1 MB, square-ish renders best.

Usage:
    py tools/make_workshop_cover.py            # writes all variants to local/cover_candidates/
    py tools/make_workshop_cover.py --pick B   # also copies that variant to assets/workshop_preview.jpg
"""
import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / 'local' / 'artwork_amgoz1' / 'patchlogo_v096_hq.jpg'
OUT_DIR = REPO / 'local' / 'cover_candidates'
FINAL = REPO / 'assets' / 'workshop_preview.jpg'

# The "0.96" sits below the SV monogram, centred, in the lower third of the 512x214 emblem.
# Box measured off the source; generous enough to swallow the glow around the glyphs.
VERSION_BOX = (182, 110, 330, 190)          # left, top, right, bottom (generous: the glyph
                                            # glow bleeds well past the strokes; a tight box
                                            # leaves a visible ghost of the digits)
FONTS = ['constanb.ttf', 'georgiab.ttf', 'cambriab.ttf', 'timesbd.ttf']
MAGENTA = (206, 122, 232)
MAGENTA_DIM = (150, 88, 176)


def load_font(size):
    for name in FONTS:
        p = Path('C:/Windows/Fonts') / name
        if p.is_file():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()


def paint_out_version(em):
    """Cover the burned-in '0.96' with colour sampled from the emblem's own shield face.

    Sampling (rather than a flat fill) keeps the shield's mottled texture, so the patch
    does not read as a rectangle. We take a strip from just ABOVE the version glyphs -
    same material, same lighting - mirror it, and blur the seam.
    """
    l, t, r, b = VERSION_BOX
    h = b - t
    donor = em.crop((l, t - h, r, t)).transpose(Image.FLIP_TOP_BOTTOM)
    donor = donor.filter(ImageFilter.GaussianBlur(2.5))
    patch = Image.new('RGB', (r - l, b - t))
    patch.paste(donor, (0, 0))
    # feathered mask so the patch edges melt into the shield instead of cutting a box
    mask = Image.new('L', (r - l, b - t), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([4, 4, r - l - 5, b - t - 5], radius=14, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(7))
    em = em.copy()
    em.paste(patch, (l, t), mask)
    return em


def glow_text(canvas, xy, text, font, fill, glow=MAGENTA, radius=9, passes=3):
    """Draw text with a soft magenta bloom, matching the emblem's own lit-glyph treatment."""
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=glow + (255,), anchor='mm')
    blurred = layer.filter(ImageFilter.GaussianBlur(radius))
    for _ in range(passes):
        canvas.alpha_composite(blurred)
    d2 = ImageDraw.Draw(canvas)
    d2.text(xy, text, font=font, fill=fill + (255,), anchor='mm')


def backdrop(size):
    """Dark vignette background in the emblem's palette."""
    w, h = size
    bg = Image.new('RGB', size, (11, 8, 14))
    d = ImageDraw.Draw(bg)
    # faint radial-ish wash behind the emblem
    for i in range(28, 0, -1):
        f = i / 28.0
        rr = int(min(w, h) * 0.62 * f)
        col = (int(11 + 34 * (1 - f)), int(8 + 16 * (1 - f)), int(14 + 44 * (1 - f)))
        d.ellipse([w // 2 - rr, h // 2 - rr, w // 2 + rr, h // 2 + rr], fill=col)
    return bg.filter(ImageFilter.GaussianBlur(26))


def build(variant, size=640):
    em = Image.open(SRC).convert('RGB')
    em = paint_out_version(em)

    canvas = backdrop((size, size)).convert('RGBA')
    # upscale the emblem to fill the width, keeping aspect
    target_w = int(size * 0.98)
    scale = target_w / em.width
    em_r = em.resize((target_w, int(em.height * scale)), Image.LANCZOS)

    # Paste the emblem at full fidelity (its own surround is already dark and mottled, so it
    # sits on the backdrop naturally); feather only the outer edge so the source rectangle's
    # border does not read as a seam. Screen-blending here washed the shield out - do not.
    ex, ey = (size - em_r.width) // 2, int(size * 0.20)
    edge = Image.new('L', em_r.size, 0)
    ImageDraw.Draw(edge).rectangle([6, 6, em_r.width - 7, em_r.height - 7], fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(9))
    emb = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    emb.paste(em_r.convert('RGBA'), (ex, ey))
    full_mask = Image.new('L', canvas.size, 0)
    full_mask.paste(edge, (ex, ey))
    emb.putalpha(full_mask)
    canvas = Image.alpha_composite(canvas, emb)

    if variant == 'A':
        # subtitle inside the emblem where "0.96" was, plus the mod name beneath
        glow_text(canvas, (size // 2, int(size * 0.20) + int(147 * scale)), 'CLASSIC',
                  load_font(int(size * 0.070)), MAGENTA)
        glow_text(canvas, (size // 2, int(size * 0.83)), 'SOULVIZIER',
                  load_font(int(size * 0.098)), (236, 226, 244), radius=11)
        glow_text(canvas, (size // 2, int(size * 0.915)), 'ANNIVERSARY EDITION',
                  load_font(int(size * 0.042)), MAGENTA_DIM, radius=7, passes=2)
    elif variant == 'B':
        # emblem-forward: nothing added inside the shield, name below
        glow_text(canvas, (size // 2, int(size * 0.80)), 'SOULVIZIER',
                  load_font(int(size * 0.108)), (236, 226, 244), radius=11)
        glow_text(canvas, (size // 2, int(size * 0.885)), 'CLASSIC',
                  load_font(int(size * 0.072)), MAGENTA)
        glow_text(canvas, (size // 2, int(size * 0.955)), 'ANNIVERSARY EDITION',
                  load_font(int(size * 0.038)), MAGENTA_DIM, radius=6, passes=2)
    elif variant == 'C':
        # minimal: emblem + CLASSIC in the version slot only, no lower text
        glow_text(canvas, (size // 2, int(size * 0.20) + int(147 * scale)), 'CLASSIC',
                  load_font(int(size * 0.078)), MAGENTA)

    return canvas.convert('RGB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pick', choices=['A', 'B', 'C'], help='also install this variant as the shipping preview')
    args = ap.parse_args()

    if not SRC.is_file():
        raise SystemExit(f'source emblem not found: {SRC}')
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    made = []
    for v in ('A', 'B', 'C'):
        img = build(v)
        p = OUT_DIR / f'cover_{v}.jpg'
        img.save(p, 'JPEG', quality=92, optimize=True)
        made.append((v, p, p.stat().st_size, img.size))
        print(f'variant {v}: {p}  {img.size[0]}x{img.size[1]}  {p.stat().st_size/1024:.0f} KB')

    if args.pick:
        chosen = OUT_DIR / f'cover_{args.pick}.jpg'
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(chosen, FINAL)
        print(f'\ninstalled variant {args.pick} -> {FINAL} ({FINAL.stat().st_size/1024:.0f} KB)')
        print('next: scripts/upload_workshop.ps1 picks it up automatically as the cover image.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
