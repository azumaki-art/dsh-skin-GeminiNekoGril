# -*- coding: utf-8 -*-
"""Final asset processor for Gemini skin with user's new assets.
"""
import os
import numpy as np
from PIL import Image
from collections import deque

BASE = r"C:\Users\shxvx\.dsh\skin-src\dsh-skin-gemini"
ASSET_DIR = os.path.join(BASE, "assets")
NEW_DIR = os.path.join(ASSET_DIR, "new_assets")

def process_char_dark():
    src_path = os.path.join(NEW_DIR, "紫の星図を読む猫耳少女.png")
    img = Image.open(src_path).convert("RGB")
    arr = np.array(img).astype(np.float32)
    h, w, _ = arr.shape

    c_max = np.max(arr, axis=-1)
    c_min = np.min(arr, axis=-1)
    sat = np.zeros_like(c_max)
    sat[c_max > 0] = (c_max[c_max > 0] - c_min[c_max > 0]) / c_max[c_max > 0]
    brightness = c_min

    # Base background: sat < 0.08 and brightness >= 212
    is_bg = (sat < 0.08) & (brightness >= 212)

    # Outer margins: allow glow
    cols = np.arange(w)[None, :]
    is_bg |= (((cols < 220) | (cols > 750)) & (sat < 0.24) & (brightness >= 200))

    # Protect core character area
    is_bg[360:680, 280:720] = False

    visited = np.zeros((h, w), dtype=bool)
    q = deque()

    for r in range(h):
        for c in [0, w-1]:
            if is_bg[r, c] and not visited[r, c]:
                visited[r, c] = True
                q.append((r, c))
    for c in range(w):
        for r in [0, h-1]:
            if is_bg[r, c] and not visited[r, c]:
                visited[r, c] = True
                q.append((r, c))

    seeds = [(260, 150), (270, 850), (520, 920), (180, 800), (330, 850), (280, 180), (260, 240), (270, 100)]
    for r, c in seeds:
        if 0 <= r < h and 0 <= c < w and is_bg[r, c] and not visited[r, c]:
            visited[r, c] = True
            q.append((r, c))

    while q:
        r, c = q.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                if is_bg[nr, nc] and not visited[nr, nc]:
                    visited[nr, nc] = True
                    q.append((nr, nc))

    alpha = np.ones((h, w), dtype=np.float32)
    alpha[visited] = 0.0

    # Edge feathering
    out_rgb = arr.copy()
    for r in range(h):
        for c in range(w):
            if not visited[r, c]:
                has_bg_neighbor = False
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and visited[nr, nc]:
                        has_bg_neighbor = True
                        break
                if has_bg_neighbor and sat[r, c] < 0.15 and brightness[r, c] > 205:
                    a = min(1.0, max(0.0, sat[r, c] / 0.15))
                    alpha[r, c] = a
                    if a > 0.05:
                        out_rgb[r, c] = np.clip((arr[r, c] - (1.0 - a) * 245.0) / a, 0, 255)

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)

    # 1px border safety
    rgba[0, :, 3] = 0
    rgba[-1, :, 3] = 0
    rgba[:, 0, 3] = 0
    rgba[:, -1, 3] = 0

    res = Image.fromarray(rgba, "RGBA")
    out_path = os.path.join(ASSET_DIR, "character-dark.png")
    res.save(out_path, "PNG")
    print("Saved character-dark.png:", res.size)

def process_char_light():
    src_path = os.path.join(NEW_DIR, "星空ホログラムの猫耳魔法使い.png")
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im)
    # 1px border safety
    arr[0, :, 3] = 0
    arr[-1, :, 3] = 0
    arr[:, 0, 3] = 0
    arr[:, -1, 3] = 0
    res = Image.fromarray(arr, "RGBA")
    out_path = os.path.join(ASSET_DIR, "character-light.png")
    res.save(out_path, "PNG")
    print("Saved character-light.png:", res.size)

def process_backgrounds():
    bg_dark = Image.open(os.path.join(NEW_DIR, "双子星の天空と星雲の対話_dark.png")).convert("RGB")
    bg_light = Image.open(os.path.join(NEW_DIR, "双子星の天空と星雲の対話_light.png")).convert("RGB")
    bg_dark.save(os.path.join(ASSET_DIR, "bg-dark.png"), "PNG")
    bg_light.save(os.path.join(ASSET_DIR, "bg-light.png"), "PNG")
    print("Saved bg-dark.png:", bg_dark.size)
    print("Saved bg-light.png:", bg_light.size)

def process_favicon():
    src_path = os.path.join(NEW_DIR, "favion_new.png")
    im = Image.open(src_path).convert("RGBA")
    # Make a clean square canvas centered
    w, h = im.size
    side = max(w, h)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(im, ((side - w) // 2, (side - h) // 2))
    fav = sq.resize((64, 64), Image.Resampling.LANCZOS)
    fav.save(os.path.join(ASSET_DIR, "favicon.png"), "PNG")
    print("Saved favicon.png:", fav.size)

if __name__ == "__main__":
    process_char_dark()
    process_char_light()
    process_backgrounds()
    process_favicon()
