"""Refresh shared branding, footer and illustrated persona pool, preserving page content."""
import json
import re
from pathlib import Path


def build_persona_pool(here):
    dist = here / "dist"
    data = json.loads((dist / "site.json").read_text())
    icons = json.loads((dist / "icons/index.json").read_text())
    personas = []
    seen = set()
    # One chance per name, including illustrated pair outcomes and custom robots.
    # Prefer a canonical link when several saved variants share the same name.
    rows = sorted(data["singles"] + data["pairs"], key=lambda r: r.get("canonical") is False)
    for row in rows:
        icon = row.get("robot_icon") or icons.get(row["id"])
        path = row.get("path")
        name = row["judge"]["name"].strip()
        if not icon or not path or not name or name.casefold() in seen:
            continue
        if not re.fullmatch(r"icons/[A-Za-z0-9_-]+\.svg", icon):
            continue
        if not re.fullmatch(r"[np]/[A-Za-z0-9_-]+/", path):
            continue
        if (dist / icon).is_file() and (dist / path / "index.html").is_file():
            seen.add(name.casefold())
            personas.append({"name": name, "path": path, "icon": icon})
    (dist / "footer-personas.json").write_text(json.dumps(personas, ensure_ascii=False, indent=2) + "\n")
    return personas


def build_footer():
    here = Path(__file__).resolve().parent
    dist = here / "dist"
    template = (here / "templates/footer.html").read_text()
    brand_template = (here / "templates/brand.html").read_text()
    personas = build_persona_pool(here)

    pages = [dist / "index.html", dist / "about/index.html", dist / "mirror/index.html", dist / "when-where/index.html", *dist.glob("n/*/index.html"), *dist.glob("p/*/index.html")]
    for page in pages:
        if not page.is_file():
            continue
        prefix = "../" * (len(page.relative_to(dist).parts) - 1)
        footer = template.replace("{{root}}", prefix)
        html = page.read_text()
        html = html.replace("Talkie Neuron Persona Library", "Talkie Persona Library").replace("Talkie Neuron Library", "Talkie Persona Library")
        html = html.replace("<title>TalkieAtlas · Neuron Persona Library</title>", "<title>Talkie Persona Library</title>")
        brand = brand_template.replace("{{root}}", prefix).strip()
        html = re.sub(r'<a\b[^>]*class="brand"[^>]*>.*?</a>', lambda _: brand, html, count=1, flags=re.S)
        brand_script = f'<script src="{prefix}branding.js" defer></script>'
        if brand_script not in html:
            html = html.replace("</head>", brand_script + "\n</head>")
        analytics_script = f'<script src="{prefix}analytics.js" defer></script>'
        if analytics_script not in html:
            html = html.replace("</head>", analytics_script + "\n</head>")
        if "<!-- site-footer -->" in html:
            html = re.sub(r"<!-- site-footer -->.*?<!-- /site-footer -->", lambda _: footer, html, count=1, flags=re.S)
        elif re.search(r"<footer\b", html):
            html = re.sub(r"<footer\b[^>]*>.*?</footer>", lambda _: footer, html, count=1, flags=re.S)
        else:
            html = html.replace("</body>", footer + "\n</body>")
        stylesheet = f'<link rel="stylesheet" href="{prefix}footer.css">'
        if stylesheet not in html:
            html = html.replace("</head>", stylesheet + "\n</head>")
        page.write_text(html)
    from build_dark import build_dark
    return {"footer_pages": len(pages), "illustrated_personas": len(personas), **build_dark()}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool-only", action="store_true", help="Refresh available illustrations without rewriting pages")
    args = parser.parse_args()
    print(json.dumps({"illustrated_personas": len(build_persona_pool(Path(__file__).resolve().parent))}
                     if args.pool_only else build_footer()))
