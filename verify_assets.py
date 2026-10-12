# -*- coding: utf-8 -*-
"""换图后自检：确认 lib/client.js 里内联的素材与你 assets/ 里的原图一致。

用法（需带 Pillow 的解释器）：
  & "C:\\Users\\shxvx\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" verify_assets.py

检查项：
  1. 5 个已内联常量（2 张背景 + 2 张立绘 + favicon）都存在且可 base64 解码；
  2. 每张 WebP 的像素尺寸与 assets/ 下对应文件一致（防止改了图忘了重新构建）；
  3. 报告各素材内联体积与 bundle 总大小。
"""
import base64
import io
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from PIL import Image
except ImportError:
    print("需要 Pillow：请用装有 Pillow 的解释器运行本脚本。")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
JS = os.path.join(HERE, "lib", "client.js")
ASSETS = os.path.join(HERE, "assets")

# 常量名 -> (assets 下的文件名, 是否 webp)
EXPECTED = {
    "GEMINI_BG_LIGHT": ("bg-light.png", True),
    "GEMINI_BG_DARK": ("bg-dark.png", True),
    "GEMINI_CHAR_LIGHT": ("character-light.png", True),
    "GEMINI_CHAR_DARK": ("character-dark.png", True),
    "GEMINI_FAVICON": ("favicon.png", False),
}


def main():
    if not os.path.exists(JS):
        print("找不到 lib/client.js，请先运行 build_client.py")
        return 1
    with open(JS, "r", encoding="utf-8") as f:
        src = f.read()
    print("client.js: %d 字节 (%.2f MB)" % (len(src), len(src) / 1048576))
    print()
    bad = 0
    for name, (fname, is_webp) in EXPECTED.items():
        m = re.search(r'const %s = "(data:image/(\w+);base64,[A-Za-z0-9+/=]+)";' % name, src)
        if not m:
            print("%-20s 缺失！bundle 里找不到该常量" % name)
            bad += 1
            continue
        raw = base64.b64decode(m.group(1).split(",", 1)[1])
        note = ""
        if is_webp:
            embedded = Image.open(io.BytesIO(raw))
            disk_path = os.path.join(ASSETS, fname)
            if os.path.exists(disk_path):
                disk = Image.open(disk_path)
                if embedded.size != disk.size:
                    note = "尺寸不一致！bundle=%s, assets/%s=%s -> 需要重新构建" % (
                        embedded.size, fname, disk.size)
                    bad += 1
                else:
                    note = "与 assets/%s 一致 (%dx%d)" % (fname, disk.size[0], disk.size[1])
            else:
                note = "assets/%s 不存在" % fname
                bad += 1
            size_txt = "%dx%d" % embedded.size
        else:
            note = "PNG favicon"
            size_txt = "-"
        print("%-20s %-9s %8.1f KB  %s  %s" % (name, m.group(2), len(raw) / 1024, size_txt, note))
    print()
    print("结论：%s" % ("全部一致，换图已生效。" if bad == 0 else "有 %d 处问题，见上。" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
