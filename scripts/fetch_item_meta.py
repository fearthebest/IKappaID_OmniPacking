"""Fetch Icon + WorldStaticModel from pzfans item pages (B42)."""
import re
import sys
import time
import urllib.request

ATTR_RE = {
    "icon": re.compile(r"<code>Icon</code></td>\s*<td><code>([^<]+)</code>", re.I),
    "wsm": re.compile(r"<code>WorldStaticModel</code></td>\s*<td><code>([^<]+)</code>", re.I),
    "static": re.compile(r"<code>StaticModel</code></td>\s*<td><code>([^<]+)</code>", re.I),
    "category": re.compile(r"<code>DisplayCategory</code></td>\s*<td><code>([^<]+)</code>", re.I),
    "item_type": re.compile(r"<code>ItemType</code></td>\s*<td><code>([^<]+)</code>", re.I),
    "tags": re.compile(r"<code>Tags</code></td>\s*<td><code>([^<]+)</code>", re.I),
    "use_delta": re.compile(r"<code>UseDelta</code></td>", re.I),
}


def fetch_meta(short: str) -> dict:
    url = f"https://pzfans.com/en/wiki/items/Base/{short}/"
    req = urllib.request.Request(url, headers={"User-Agent": "IKOP-meta/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except OSError as exc:
        return {"error": str(exc)}

    meta = {}
    for key, pat in ATTR_RE.items():
        m = pat.search(html)
        if not m:
            continue
        if key == "use_delta":
            meta[key] = True
        else:
            meta[key] = m.group(1)
    return meta


def main():
    names = sys.argv[1:]
    for short in names:
        meta = fetch_meta(short)
        print(short, meta)
        time.sleep(0.15)


if __name__ == "__main__":
    main()
