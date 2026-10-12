# -*- coding: utf-8 -*-
"""gemini-starlight-neko 皮肤构建器：素材(PNG) -> WebP data URI + 内联 CSS -> lib/client.js。

用法：
  python build_client.py
"""
import base64
import io
import json
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(HERE, "assets")
CSS_FILE = os.path.join(HERE, "gemini.css")
OUT = os.path.join(HERE, "lib", "client.js")

PLUGIN_ID = "@dsh-external/dsh-client-ui-skin-gemini"
SKIN_SCOPE = "data-dsh-gemini-skin"
TITLE = "Gemini · DeepSeek Harness"
TAG_ID = "@dsh-external/dsh-client-ui-skin-gemini/gemini-skin.css"

REQUIRED_ASSETS = {
    "GEMINI_BG_LIGHT": ("bg-light.png", "--gemini-bg-art 浅色"),
    "GEMINI_BG_DARK": ("bg-dark.png", "--gemini-bg-art 深色"),
    "GEMINI_CHAR_LIGHT": ("character-light.png", "星空全息猫耳魔法使（浅色白天立绘）"),
    "GEMINI_CHAR_DARK": ("character-dark.png", "紫之星图猫耳少女（深色黑夜立绘）"),
}
FAVICON_FILE = os.path.join(ASSET_DIR, "favicon.png")


def to_webp_data_uri(png_path, quality=85):
    from PIL import Image
    img = Image.open(png_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def to_png_data_uri(png_path):
    with open(png_path, "rb") as f:
        data = f.read()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def css_escaped(css):
    """CSS 内联进 JS 字符串字面量：转义反斜杠、双引号与换行。"""
    return (css.replace("\\", "\\\\")
               .replace('"', '\\"')
               .replace("\r", "")
               .replace("\n", "\\n"))


JS_TEMPLATE = r"""window.__ModuleLoader__.load({
	id: "__PLUGIN_ID__",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });

__ASSETS__

		//#region css
		const css = "__CSS__";
		const tagId = "__TAG_ID__";
		if (typeof document !== "undefined" && document.querySelector("style[data-plugin-css=" + JSON.stringify(tagId) + "]") === null) {
			const tag = document.createElement("style");
			tag.dataset.plugin = "__PLUGIN_ID__";
			tag.dataset.pluginCss = tagId;
			tag.textContent = css;
			document.head.appendChild(tag);
		}
		//#endregion

		const SKIN_SCOPE = "__SKIN_SCOPE__";
		const SKIN_TITLE = "__TITLE__";
		const CONV_SEL = ":is([data-pane='conversation'], [class*='centerCol'])";
		const SIDEBAR_SEL = ":is([data-pane='sidebar'], [class*='sidebarCol'])";

		function apply(ctx) {
			const body = document.body;
			const previous = new Map();
			for (const p of ["--gemini-bg-art"]) previous.set(p, body.style.getPropertyValue(p));
			const originalTitle = document.title;

			const character = document.createElement("img");
			character.dataset.geminiCharacter = "";
			character.alt = "";
			character.src = body.hasAttribute("data-ds-dark-theme") ? GEMINI_CHAR_DARK : GEMINI_CHAR_LIGHT;

			const corners = document.createElement("div");
			corners.dataset.skinChrome = "gemini-corners";
			for (const pos of ["top-left", "top-right", "bottom-left", "bottom-right"]) {
				const s = document.createElement("span");
				s.dataset.skinCorner = pos;
				corners.append(s);
			}

			const seat = () => {
				const chat = document.querySelector(CONV_SEL);
				if (chat && character.parentElement !== chat) chat.prepend(character);
				const sb = document.querySelector(SIDEBAR_SEL);
				const root = sb ? sb.querySelector(":scope > div") : null;
				if (root && corners.parentElement !== root) root.prepend(corners);
			};

			const syncTheme = () => {
				const isDark = body.hasAttribute("data-ds-dark-theme");
				const bgSrc = isDark ? GEMINI_BG_DARK : GEMINI_BG_LIGHT;
				const charSrc = isDark ? GEMINI_CHAR_DARK : GEMINI_CHAR_LIGHT;
				body.style.setProperty("--gemini-bg-art", "url(" + bgSrc + ")");
				if (character.src !== charSrc) {
					character.src = charSrc;
				}
			};

			body.setAttribute(SKIN_SCOPE, "");
			syncTheme();
			seat();

			const attrObs = new MutationObserver((records) => {
				for (const r of records) {
					if (r.type === "attributes" && r.attributeName === "data-ds-dark-theme" && r.target === body) {
						syncTheme();
					}
				}
			});
			attrObs.observe(body, { attributes: true, attributeFilter: ["data-ds-dark-theme"] });

			let frame = 0;
			const structObs = new MutationObserver(() => {
				if (frame) return;
				frame = requestAnimationFrame(() => {
					frame = 0;
					seat();
				});
			});
			structObs.observe(body, { childList: true, subtree: true });

			const favicon = document.createElement("link");
			favicon.rel = "icon";
			favicon.href = GEMINI_FAVICON;
			document.head.append(favicon);
			document.title = SKIN_TITLE;

			ctx.effect(() => () => {
				attrObs.disconnect();
				structObs.disconnect();
				if (frame) cancelAnimationFrame(frame);
				character.remove();
				corners.remove();
				favicon.remove();
				for (const [p, v] of previous) body.style.setProperty(p, v);
				body.removeAttribute(SKIN_SCOPE);
				if (document.title === SKIN_TITLE) document.title = originalTitle;
			}, "gemini-starlight-neko: skin");
		}
		exports.apply = apply;
		return module.exports;
	}
});
"""


def main():
    missing = [name for name, (f, _) in REQUIRED_ASSETS.items() if not os.path.exists(os.path.join(ASSET_DIR, f))]
    if missing:
        print("缺失必要素材:", [(f, label) for name, (f, label) in REQUIRED_ASSETS.items() if name in missing])
        sys.exit(1)

    with open(CSS_FILE, "r", encoding="utf-8") as f:
        raw_css = f.read()

    assets_lines = []
    for name, (fname, label) in REQUIRED_ASSETS.items():
        fpath = os.path.join(ASSET_DIR, fname)
        uri = to_webp_data_uri(fpath)
        assets_lines.append(f"\t\tconst {name} = {json.dumps(uri)};")
        print(f"已内嵌素材: {label} ({fname}) -> WebP data URI (体积: {len(uri)//1024} KB)")

    if os.path.exists(FAVICON_FILE):
        fav_uri = to_png_data_uri(FAVICON_FILE)
        assets_lines.append(f"\t\tconst GEMINI_FAVICON = {json.dumps(fav_uri)};")
        print(f"已内嵌 Favicon: {FAVICON_FILE} -> PNG data URI")
    else:
        print("警告: favicon.png 缺失")
        assets_lines.append('\t\tconst GEMINI_FAVICON = "";')

    assets_block = "\n".join(assets_lines)

    js = (JS_TEMPLATE
          .replace("__ASSETS__", assets_block)
          .replace("__CSS__", css_escaped(raw_css))
          .replace("__TAG_ID__", TAG_ID)
          .replace("__PLUGIN_ID__", PLUGIN_ID)
          .replace("__SKIN_SCOPE__", SKIN_SCOPE)
          .replace("__TITLE__", TITLE))

    os.makedirs(os.path.join(HERE, "lib"), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)

    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print("构建成功:", OUT)
    print("Bundle 最终体积: %.2f MB" % size_mb)


if __name__ == "__main__":
    main()
