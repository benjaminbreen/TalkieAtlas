"""Derive the dark theme from the light stylesheets and install the theme switch on every page.

The light CSS is hand-written with many literal colors. Rather than maintaining a parallel
dark stylesheet, this script reads every color-bearing declaration, maps its colors to dark
equivalents, and writes the result under :root[data-theme="dark"]. theme.js sets data-theme
from the visitor's saved choice or, by default, their system setting. Re-run after editing
the light CSS; generated sections are replaced, never duplicated.
"""
import colorsys
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
CSS_FILES = ["style.css", "typography.css", "footer.css"]
CSS_START, CSS_END = "/* dark:auto (build_dark.py) */", "/* /dark:auto */"
STYLE_RE = re.compile(r'\n?<style id="dark-auto">.*?</style>', re.S)
PREFIX = ':root[data-theme="dark"]'
COLOR_PROPS = re.compile(r"^(color|background(-color|-image)?|border(-(top|right|bottom|left|block|inline)(-start|-end)?)?(-color)?|outline(-color)?|box-shadow|text-shadow|"
                         r"fill|stroke|stop-color|text-decoration(-color)?|caret-color|accent-color|scrollbar-color|"
                         r"column-rule(-color)?|--[\w-]+)$")
TEXT_PROPS = {"color", "text-decoration", "text-decoration-color", "outline", "outline-color", "caret-color", "fill"}
BG_PROPS = {"background", "background-color", "background-image"}
LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:white|black)\b|rgba?\([^)]*\)")

# Hand-tuned tokens. They follow the generated rules, so they win over the mechanical mapping.
TOKENS = {
    "style.css": """:root[data-theme="dark"]{color-scheme:dark;--ink:#ececee;--muted:#9a9aa1;--line:#2c2c30;--paper:#111113;--panel:#1c1c1f;--blue:#2f95ff;--normal:#7d838c}
:root[data-theme="dark"] header{background:#111113ed}
:root[data-theme="dark"] .pill.black{background:#ececee;border-color:#ececee;color:#111113}""",
    "typography.css": """:root[data-theme="dark"]{--muted:#a3a3ab}""",
    "footer.css": """:root[data-theme="dark"] .site-footer{background:#18181a;border-top-color:#2c2c30}""",
}


def parse_color(text):
    t = text.lower()
    if t == "white":
        return 1, 1, 1, 1
    if t == "black":
        return 0, 0, 0, 1
    if t.startswith("#"):
        h = t[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1
        return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a
    parts = re.findall(r"[\d.]+%?", t)
    if len(parts) < 3:
        return None
    rgb = [float(p[:-1]) / 100 if p.endswith("%") else float(p) / 255 for p in parts[:3]]
    a = float(parts[3][:-1]) / 100 if len(parts) > 3 and parts[3].endswith("%") else float(parts[3]) if len(parts) > 3 else 1
    return (*rgb, a)


def fmt(r, g, b, a):
    hx = "#" + "".join(f"{round(max(0, min(1, v)) * 255):02x}" for v in (r, g, b))
    return hx if a >= 0.999 else hx + f"{round(a * 255):02x}"


def lightness(value):
    c = parse_color(value) if value else None
    return colorsys.rgb_to_hls(*c[:3])[1] if c else None


def dark_color(value, prop):
    c = parse_color(value)
    if not c:
        return value
    r, g, b, a = c
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if l < 0.12 and a < 1:  # shadows and scrims stay dark
        return fmt(r, g, b, min(1, a * 1.8))
    if prop == "color" and l > 0.95:  # white text sits on a colored fill; dark_rule handles fills that turn light
        return value
    if max(r, g, b) - min(r, g, b) < 0.09:  # neutral: invert lightness, keeping its slight warm or cool cast
        nl = 0.16 if prop in BG_PROPS and l > 0.99 else min(0.93, 0.07 + 0.9 * (1 - l))
    elif prop in TEXT_PROPS and l < 0.6:
        nl = 0.68
    elif prop in BG_PROPS and l > 0.85:
        nl, s = 0.24, s * 0.6
    else:
        return value
    return fmt(*colorsys.hls_to_rgb(h, nl, s), a)


def split_top(text, sep):
    out, depth, cur, quote = [], 0, "", None
    for ch in text:
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == sep and depth == 0:
            out.append(cur)
            cur = ""
            continue
        cur += ch
    out.append(cur)
    return out


def prefix_selector(sel):
    sel = sel.strip()
    for root in (":root", "html"):
        if sel == root or sel.startswith(root) and not sel[len(root)].isalnum() and sel[len(root)] != "-":
            return PREFIX + sel[len(root):]
    return f"{PREFIX} {sel}"


def blocks(css):
    """Yield (prelude, body) for top-level blocks; bodies of at-rules are returned raw."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    i, n = 0, len(css)
    while i < n:
        start = css.find("{", i)
        if start < 0:
            return
        depth, j = 1, start + 1
        while j < n and depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        yield css[i:start].strip().split(";")[-1].strip(), css[start + 1:j - 1]
        i = j


def dark_rule(prelude, body):
    decls = []
    for decl in split_top(body, ";"):
        if ":" not in decl:
            continue
        prop, value = (x.strip() for x in decl.split(":", 1))
        if COLOR_PROPS.match(prop.lower()) and (not prop.startswith("--") or LITERAL.search(value)):
            decls.append([prop.lower(), value, LITERAL.sub(lambda m: dark_color(m.group(), prop.lower()), value)])
    if not decls:
        return ""
    # White text on a surface that is now light (a dark chip, or --ink) needs to turn dark too.
    bg = next((d for d in decls if d[0] in BG_PROPS), None)
    bg_light = bg and ("var(--ink)" in bg[1] or (lightness(LITERAL.search(bg[2]).group() if LITERAL.search(bg[2]) else None) or 0) > 0.6)
    for d in decls:
        if d[0] == "color" and bg_light and (lightness(d[1]) or 0) > 0.95:
            d[2] = "#111113"
    selectors = ",".join(prefix_selector(s) for s in split_top(prelude, ","))
    return selectors + "{" + ";".join(f"{p}:{v}" for p, _, v in decls) + "}"


def dark_css(css):
    out = []
    for prelude, body in blocks(css):
        if prelude.startswith(("@media", "@supports")):
            inner = dark_css(body)
            if inner:
                out.append(prelude + "{" + inner + "}")
        elif not prelude.startswith("@"):
            rule = dark_rule(prelude, body)
            if rule:
                out.append(rule)
    return "\n".join(out)


def strip_section(css):
    return re.sub(r"\n*" + re.escape(CSS_START) + r".*?" + re.escape(CSS_END) + r"\n?", "\n", css, flags=re.S).rstrip() + "\n"


def install_css(dist):
    for name in CSS_FILES:
        path = dist / name
        light = strip_section(path.read_text())
        section = dark_css(light) + "\n" + TOKENS.get(name, "")
        path.write_text(f"{light}\n{CSS_START}\n{section.strip()}\n{CSS_END}\n")


def install_pages(dist):
    pages = 0
    for page in dist.rglob("*.html"):
        html = page.read_text()
        if "</head>" not in html:
            continue
        prefix = "../" * (len(page.relative_to(dist).parts) - 1)
        html = STYLE_RE.sub("", html)
        inline = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, flags=re.S))
        generated = dark_css(inline) if inline else ""
        if generated:
            last = html.rfind("</style>") + len("</style>")
            html = html[:last] + f'\n<style id="dark-auto">{generated}</style>' + html[last:]
        # The theme must be set before first paint, so theme.js loads blocking, ahead of the stylesheets.
        script = f'<script src="{prefix}theme.js"></script>'
        html = re.sub(r'<script src="(\.\./)*theme\.js"></script>\n?', "", html)
        html = re.sub(r'<link rel="stylesheet" href="(\.\./)*theme\.css">\n?', "", html)
        head = re.search(r"<head[^>]*>", html)
        meta = re.search(r'<meta name="viewport"[^>]*>', html)
        anchor = meta.end() if meta else head.end()
        html = html[:anchor] + script + html[anchor:]
        html = html.replace("</head>", f'<link rel="stylesheet" href="{prefix}theme.css">\n</head>', 1)
        page.write_text(html)
        pages += 1
    return pages


def build_dark(dist=DIST):
    install_css(dist)
    return {"dark_pages": install_pages(dist)}


if __name__ == "__main__":
    # Optional argument: another copy of the site, such as a deploy checkout's public/.
    print(json.dumps(build_dark(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DIST)))
