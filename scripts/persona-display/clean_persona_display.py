"""Remove generated review blocks from existing entry pages without rebuilding other UI."""
import argparse
import json
from pathlib import Path
import re


def clean_pages(root):
    pages = sorted([*root.glob("n/*/index.html"), *root.glob("p/*/index.html")])
    changed = 0
    removed = 0
    for path in pages:
        before = path.read_text()
        after, count = re.subn(r'\s*<p class="(?:tags|ranking-note(?: small)?)">.*?</p>', "", before, flags=re.S)
        after = re.sub(r'\s*<p class="detail-description">\s*</p>', "", after)
        after = re.sub(r'(<p class="footer-colophon">)(.*?)(</p>)',
                       lambda m: m[1] + m[2].replace("Earlier replies rated by GPT-6 Luna; new discoveries selected and rated by Codex. ", "") + m[3],
                       after, flags=re.S)
        # These fields are factual content/settings, not review-display annotations.
        for pattern in [r'<p class="reply dropcap">.*?</p>', r'<dl class="stats">.*?</dl>']:
            assert re.findall(pattern, before, re.S) == re.findall(pattern, after, re.S), path
        descriptions = lambda html: [s for s in re.findall(r'<p class="detail-description">(.*?)</p>', html, re.S) if s.strip()]
        assert descriptions(before) == descriptions(after), path
        if after != before:
            path.write_text(after)
            changed += 1
        removed += count
    return {"entry_pages_checked": len(pages), "entry_pages_cleaned": changed,
            "review_blocks_removed": removed, "raw_reply_description_and_score_blocks_unchanged": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Rendered static-site directory")
    args = parser.parse_args()
    print(json.dumps(clean_pages(args.root)))
