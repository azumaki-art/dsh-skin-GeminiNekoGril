# -*- coding: utf-8 -*-
"""Precision cutout and asset generation for Gemini Starlight Neko skin.
"""
import os
import numpy as np
from PIL import Image, ImageFilter
from collections import deque

BASE = r"C:\Users\shxvx\.dsh\skin-src\dsh-skin-gemini"
ASSET_DIR = os.path.join(BASE, "assets")

SRC1 = r"C:\Users\shxvx\Pictures\Screenshots\スクリーンショット 2026-10-11 115832.png"
SRC2 = r"C:\Users\shxvx\Pictures\Screenshots\スクリーンショット 2026-10-11 115852.png"

def precision_cutout(img_path, crop_box, name):
    raw = Image.open(img_path).convert("RGB")
    arr = np.array(raw)[crop_box[0]:crop_box[1], crop_box[2]:crop_box[3]]
    h, w, _ = arr.shape
    
    # Check background candidate: any pixel where R,G,B are all >= 244
    is_bg_candidate = np.all(arr >= 244, axis=-1)
    
    # Flood-fill from outer 4 borders
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    for r in range(h):
        for c in [0, w-1]:
            if is_bg_candidate[r, c] and not visited[r, c]:
                visited[r, c] = True
                q.append((r, c))
    for c in range(w):
        for r in [0, h-1]:
            if is_bg_candidate[r, c] and not visited[r, c]:
                visited[r, c] = True
                q.append((r, c))
                
    while q:
        r, c = q.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                if is_bg_candidate[nr, nc] and not visited[nr, nc]:
                    visited[nr, nc] = True
                    q.append((nr, nc))
                    
    # Also find background holes (regions between legs, under arms, around hair curls)
    hole_candidates = is_bg_candidate & (~visited)
    h_vis = np.zeros((h, w), dtype=bool)
    
    for r in range(h):
        for c in range(w):
            if hole_candidates[r, c] and not h_vis[r, c]:
                cluster = []
                hq = deque([(r, c)])
                h_vis[r, c] = True
                while hq:
                    cr, cc = hq.popleft()
                    cluster.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and hole_candidates[nr, nc] and not h_vis[nr, nc]:
                            h_vis[nr, nc] = True
                            hq.append((nr, nc))
                
                ys = [p[0] for p in cluster]
                xs = [p[1] for p in cluster]
                min_y, max_y = min(ys), max(ys)
                min_x, max_x = min(xs), max(xs)
                
                # Check if it's the socks (socks in char1/char2 are at y>360, x in [100..210])
                is_sock = (min_y > 360 and min_x > 95 and max_x < 215)
                if not is_sock and len(cluster) >= 10:
                    for pr, pc in cluster:
                        visited[pr, pc] = True

    # Build alpha map
    alpha = np.ones((h, w), dtype=np.float32)
    alpha[visited] = 0.0
    
    # Smooth edge transitions for unvisited boundary pixels
    out_rgb = arr.astype(np.float32).copy()
    for r in range(h):
        for c in range(w):
            if not visited[r, c]:
                # Check if this pixel neighbors a background pixel
                has_bg_neighbor = False
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and visited[nr, nc]:
                        has_bg_neighbor = True
                        break
                if has_bg_neighbor:
                    # Distance to pure white
                    d = 255.0 - np.min(arr[r, c])
                    if d < 48:
                        a = max(0.0, d / 48.0)
                        alpha[r, c] = a
                        if a > 0.08:
                            # Decontaminate white background bleed
                            out_rgb[r, c] = np.clip((arr[r, c] - (1.0 - a) * 255.0) / a, 0, 255)
                        else:
                            alpha[r, c] = 0.0
                            
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255).astype(np.uint8)
    
    res = Image.fromarray(rgba, "RGBA")
    
    # 2x supersampling with Lanczos
    w2, h2 = int(w * 2), int(h * 2)
    res_scaled = res.resize((w2, h2), Image.Resampling.LANCZOS)
    return res_scaled

# Exact crops excluding any window borders
out1 = precision_cutout(SRC1, (4, 521, 21, 311), "char_dark (tall)")
out2 = precision_cutout(SRC2, (7, 524, 18, 308), "char_light (chibi)")

out1_path = os.path.join(ASSET_DIR, "character-dark.png")
out2_path = os.path.join(ASSET_DIR, "character-light.png")

out1.save(out1_path, "PNG")
out2.save(out2_path, "PNG")

print("Saved clean character-dark:", out1_path, out1.size)
print("Saved clean character-light:", out2_path, out2.size)
