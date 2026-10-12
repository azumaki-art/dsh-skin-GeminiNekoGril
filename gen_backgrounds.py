# -*- coding: utf-8 -*-
"""Generate high-aesthetic starry background art and favicon for Gemini skin.
"""
import math
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = r"C:\Users\shxvx\.dsh\skin-src\dsh-skin-gemini"
ASSET_DIR = os.path.join(BASE, "assets")

def create_four_point_star(size, outer_color, inner_color):
    """Draw a four-pointed Gemini starlight sparkle."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    cx, cy = size / 2.0, size / 2.0
    r_outer = size * 0.48
    r_inner = size * 0.08
    
    # 8-point polygon: 4 long arms + 4 short inner indentations
    points = []
    for i in range(8):
        angle = i * (math.pi / 4.0)
        r = r_outer if (i % 2 == 0) else r_inner
        px = cx + r * math.sin(angle)
        py = cy - r * math.cos(angle)
        points.append((px, py))
        
    draw.polygon(points, fill=outer_color)
    
    # Inner glow
    inner_points = []
    r_inner_outer = r_outer * 0.4
    r_inner_inner = r_inner * 0.35
    for i in range(8):
        angle = i * (math.pi / 4.0)
        r = r_inner_outer if (i % 2 == 0) else r_inner_inner
        px = cx + r * math.sin(angle)
        py = cy - r * math.cos(angle)
        inner_points.append((px, py))
    draw.polygon(inner_points, fill=inner_color)
    
    return im

def draw_star(base_img, cx, cy, size, outer_rgba, inner_rgba, glow_rgba=None):
    star_img = create_four_point_star(size, outer_rgba, inner_rgba)
    if glow_rgba:
        # Add blurred glow halo
        glow = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        g_draw.ellipse([size * 0.5, size * 0.5, size * 1.5, size * 1.5], fill=glow_rgba)
        glow = glow.filter(ImageFilter.GaussianBlur(size * 0.35))
        base_img.alpha_composite(glow, (int(cx - size), int(cy - size)))
    base_img.alpha_composite(star_img, (int(cx - size / 2), int(cy - size / 2)))

def generate_dark_bg(width=1920, height=1080):
    """Deep galactic purple-blue cosmic nebula with Gemini twin stars."""
    # Base gradient: dark cosmic void to deep purple nebula
    img = Image.new("RGBA", (width, height), (11, 14, 28, 255))
    
    # Render rich nebula clouds in right half (leaving left half clean for chat)
    arr = np.zeros((height, width, 4), dtype=np.float32)
    # Background base gradient
    y = np.linspace(0, 1, height)[:, None]
    x = np.linspace(0, 1, width)[None, :]
    
    # Dark blue-violet base
    arr[..., 0] = 11 + x * 15 + y * 8
    arr[..., 1] = 13 + x * 8 + y * 12
    arr[..., 2] = 27 + x * 35 + y * 25
    arr[..., 3] = 255
    
    base_pil = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    
    # Layer 1: Nebula glow layers using soft ellipses
    nebula = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(nebula)
    
    # Large soft cosmic nebula clouds concentrated on the right
    n_draw.ellipse([width * 0.55, height * 0.05, width * 1.15, height * 0.85], fill=(98, 55, 180, 75))
    n_draw.ellipse([width * 0.70, height * 0.25, width * 1.25, height * 0.95], fill=(56, 120, 240, 60))
    n_draw.ellipse([width * 0.60, height * 0.40, width * 1.05, height * 1.05], fill=(168, 85, 247, 50))
    n_draw.ellipse([width * 0.75, height * 0.15, width * 0.95, height * 0.55], fill=(79, 172, 254, 70))
    
    # Left soft ambient glow (very gentle, does not interfere with reading)
    n_draw.ellipse([width * -0.2, height * 0.6, width * 0.4, height * 1.2], fill=(45, 25, 95, 30))
    
    nebula = nebula.filter(ImageFilter.GaussianBlur(120))
    base_pil.alpha_composite(nebula)
    
    # Layer 2: Celestial Orbital Rings (Sci-Fi Constellation Astrolabe)
    rings = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(rings)
    cx, cy = int(width * 0.82), int(height * 0.45)
    
    for r, width_line, color in [
        (420, 1, (130, 160, 255, 35)),
        (340, 2, (180, 130, 255, 55)),
        (260, 1, (100, 210, 255, 45)),
        (180, 2, (255, 220, 140, 65)),
        (110, 1, (200, 160, 255, 40)),
    ]:
        r_draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width_line)
        
    # Constellation connection lines
    twin1 = (cx - 70, cy - 80)
    twin2 = (cx + 80, cy + 60)
    r_draw.line([twin1, twin2], fill=(220, 210, 255, 90), width=2)
    r_draw.line([(cx - 160, cy + 40), twin1], fill=(160, 190, 255, 60), width=1)
    r_draw.line([(cx + 150, cy - 100), twin1], fill=(180, 140, 255, 60), width=1)
    r_draw.line([(cx + 200, cy + 120), twin2], fill=(140, 200, 255, 60), width=1)
    
    base_pil.alpha_composite(rings)
    
    # Layer 3: Star clusters and Gemini Sparkle Stars
    stars = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    random.seed(42)
    s_draw = ImageDraw.Draw(stars)
    # Tiny background stars
    for _ in range(350):
        sx = random.randint(int(width * 0.35), width - 10)
        sy = random.randint(10, height - 10)
        sr = random.uniform(0.8, 2.2)
        s_alpha = random.randint(40, 180)
        s_col = random.choice([
            (200, 225, 255, s_alpha),
            (235, 210, 255, s_alpha),
            (255, 240, 190, s_alpha),
            (160, 230, 255, s_alpha),
        ])
        s_draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=s_col)
        
    base_pil.alpha_composite(stars)
    
    # Major Gemini Twin Stars (Luminous 4-point diamonds)
    draw_star(base_pil, twin1[0], twin1[1], 80, (255, 225, 140, 240), (255, 255, 255, 255), (255, 200, 100, 120))
    draw_star(base_pil, twin2[0], twin2[1], 96, (140, 210, 255, 245), (255, 255, 255, 255), (100, 180, 255, 140))
    
    # Surrounding accent stars
    draw_star(base_pil, cx - 160, cy + 40, 48, (210, 160, 255, 220), (255, 255, 255, 255), (180, 120, 255, 90))
    draw_star(base_pil, cx + 150, cy - 100, 52, (150, 230, 255, 220), (255, 255, 255, 255), (100, 200, 255, 90))
    draw_star(base_pil, cx + 200, cy + 120, 42, (255, 210, 170, 200), (255, 255, 255, 255), (255, 190, 130, 80))
    draw_star(base_pil, width * 0.62, height * 0.22, 38, (190, 180, 255, 190), (255, 255, 255, 255), (160, 140, 255, 70))
    draw_star(base_pil, width * 0.92, height * 0.72, 36, (140, 220, 255, 190), (255, 255, 255, 255), (100, 190, 255, 70))
    
    return base_pil

def generate_light_bg(width=1920, height=1080):
    """Ethereal daylight sky with subtle pastel nebula and iridescent sparkles."""
    # Base: clean crystalline daylight tint
    arr = np.zeros((height, width, 4), dtype=np.float32)
    y = np.linspace(0, 1, height)[:, None]
    x = np.linspace(0, 1, width)[None, :]
    
    # Soft porcelain sky gradient (#F4F7FD -> #EBF1FD)
    arr[..., 0] = 246 - x * 6 - y * 4
    arr[..., 1] = 248 - x * 4 - y * 3
    arr[..., 2] = 254 - x * 2 - y * 1
    arr[..., 3] = 255
    
    base_pil = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    
    # Subtle pastel nebula clouds on right
    nebula = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(nebula)
    
    n_draw.ellipse([width * 0.55, height * 0.05, width * 1.15, height * 0.85], fill=(215, 225, 255, 80))
    n_draw.ellipse([width * 0.70, height * 0.25, width * 1.25, height * 0.95], fill=(230, 215, 255, 70))
    n_draw.ellipse([width * 0.60, height * 0.40, width * 1.05, height * 1.05], fill=(210, 240, 255, 60))
    n_draw.ellipse([width * 0.75, height * 0.15, width * 0.95, height * 0.55], fill=(255, 240, 220, 50))
    
    nebula = nebula.filter(ImageFilter.GaussianBlur(130))
    base_pil.alpha_composite(nebula)
    
    # Soft orbital rings
    rings = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(rings)
    cx, cy = int(width * 0.82), int(height * 0.45)
    
    for r, width_line, color in [
        (420, 1, (160, 185, 245, 50)),
        (340, 2, (185, 165, 245, 60)),
        (260, 1, (140, 200, 250, 55)),
        (180, 2, (235, 195, 120, 75)),
        (110, 1, (185, 175, 245, 50)),
    ]:
        r_draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width_line)
        
    twin1 = (cx - 70, cy - 80)
    twin2 = (cx + 80, cy + 60)
    r_draw.line([twin1, twin2], fill=(160, 160, 235, 80), width=2)
    r_draw.line([(cx - 160, cy + 40), twin1], fill=(150, 180, 235, 60), width=1)
    r_draw.line([(cx + 150, cy - 100), twin1], fill=(175, 150, 235, 60), width=1)
    r_draw.line([(cx + 200, cy + 120), twin2], fill=(140, 195, 235, 60), width=1)
    
    base_pil.alpha_composite(rings)
    
    # Star sparkles
    draw_star(base_pil, twin1[0], twin1[1], 75, (245, 185, 75, 220), (255, 255, 255, 255), (255, 215, 120, 80))
    draw_star(base_pil, twin2[0], twin2[1], 90, (90, 165, 245, 220), (255, 255, 255, 255), (130, 195, 255, 90))
    draw_star(base_pil, cx - 160, cy + 40, 44, (170, 130, 235, 200), (255, 255, 255, 255), (195, 160, 255, 60))
    draw_star(base_pil, cx + 150, cy - 100, 48, (110, 190, 245, 200), (255, 255, 255, 255), (140, 210, 255, 60))
    draw_star(base_pil, cx + 200, cy + 120, 38, (240, 175, 110, 180), (255, 255, 255, 255), (250, 200, 150, 50))
    draw_star(base_pil, width * 0.62, height * 0.22, 34, (160, 150, 240, 170), (255, 255, 255, 255), (180, 170, 255, 50))
    
    return base_pil

def generate_favicon(size=64):
    """Generate Gemini 4-point star icon with round-corner badge."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Dark rounded badge (#13162b)
    margin = 3
    radius = 14
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, fill=(19, 22, 43, 255))
    
    # Subtle border (#7B68EE)
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, outline=(123, 104, 238, 160), width=2)
    
    # Gemini diamond star in center
    cx, cy = size / 2.0, size / 2.0
    star = create_four_point_star(int(size * 0.72), (255, 215, 110, 255), (255, 255, 255, 255))
    
    # Halo glow
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([14, 14, size - 14, size - 14], fill=(120, 150, 255, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    
    im.alpha_composite(glow)
    im.alpha_composite(star, (int(cx - star.width / 2), int(cy - star.height / 2)))
    
    return im

dark_bg = generate_dark_bg()
light_bg = generate_light_bg()
fav = generate_favicon()

dark_bg.save(os.path.join(ASSET_DIR, "bg-dark.png"), "PNG")
light_bg.save(os.path.join(ASSET_DIR, "bg-light.png"), "PNG")
fav.save(os.path.join(ASSET_DIR, "favicon.png"), "PNG")

print("Generated bg-dark.png:", dark_bg.size)
print("Generated bg-light.png:", light_bg.size)
print("Generated favicon.png:", fav.size)
