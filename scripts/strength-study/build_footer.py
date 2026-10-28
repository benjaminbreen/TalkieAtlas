"""Refresh shared branding, footer and illustrated persona pool, preserving page content."""
import json
import re
from pathlib import Path


def build_footer():
    here = Path(__file__).resolve().parent
    dist = here / "dist"
    template = (here / "templates/footer.html").read_text()
    brand_template = (here / "templates/brand.html").read_text()
    data = json.loads((dist / "site.json").read_text())
    personas = []
    seen = set()
    for row in sorted(data["singles"], key=lambda r: (bool(r.get('sprint_featured')), -r.get('featured_order',999), r["judge"]["weirdness"] or 0, r["judge"]["coherence"] or 0), reverse=True):
        if row.get('canonical') is False:continue
        slug = f"{row['layer']}-{row['neuron']}-{'up' if row['sign'] > 0 else 'down'}"
        icon = f"icons/{slug}.svg"
        name = row["judge"]["name"]
        if (dist / icon).is_file() and name.casefold() not in seen:
            seen.add(name.casefold())
            personas.append({"name": name, "path": f"n/{slug}/", "icon": icon})
        if len(personas) == 100:
            break
    (dist / "footer-personas.json").write_text(json.dumps(personas, ensure_ascii=False, indent=2) + "\n")

    pages = [dist / "index.html", dist / "about/index.html", dist / "mirror/index.html", *dist.glob("n/*/index.html"), *dist.glob("p/*/index.html")]
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
    return {"footer_pages": len(pages), "illustrated_personas": len(personas)}


if __name__ == "__main__":
    print(json.dumps(build_footer()))
