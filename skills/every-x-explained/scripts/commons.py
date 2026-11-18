#!/usr/bin/env python3
"""Search Wikimedia Commons and download images with licence info.

  commons.py search "<query>" [--n 8]            -> list candidates (title, size, licence)
  commons.py search "<query>" [--n 8] [--drawing]   (--drawing finds SVG maps/diagrams)
  commons.py get "<File:Title.jpg>" <id> <assets_dir> [--width 1600]
                                                  -> downloads to <assets_dir>/<id>.<ext>, appends manifest.json
"""
import json, os, sys, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "every-x-explained-skill/0.1 (video research tool)"

def fetch(url, timeout=30):
    """GET with polite retry: Commons answers bursts with HTTP 429."""
    import time, urllib.error
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            time.sleep(1.0)
            return data
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 5 * (attempt + 1)
            print(f"  429, waiting {wait}s", file=sys.stderr)
            time.sleep(wait)

def api(params):
    params = {**params, "format": "json", "formatversion": "2"}
    return json.loads(fetch(API + "?" + urllib.parse.urlencode(params)))

def strip(html):
    import re
    return re.sub(r"<[^>]+>", "", html or "").strip()

def dedupe(s):
    """Commons often renders the artist twice ('Unknown authorUnknown author')."""
    h = len(s) // 2
    return s[:h] if len(s) % 2 == 0 and s[:h] == s[h:] else s

def info(pages, width):
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        out.append({
            "title": p["title"],
            "width": ii.get("width"), "height": ii.get("height"),
            "mime": ii.get("mime"),
            "url": ii.get("thumburl") or ii.get("url"),
            "page": ii.get("descriptionurl"),
            "license": strip(meta.get("LicenseShortName", {}).get("value")),
            "artist": dedupe(strip(meta.get("Artist", {}).get("value")))[:120],
        })
    return out

def search(q, n=8, width=1600, kind="bitmap"):
    d = api({"action": "query", "generator": "search", "gsrsearch": f"filetype:{kind} {q}",
             "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo",
             "iiprop": "url|size|mime|extmetadata", "iiurlwidth": width})
    pages = sorted(d.get("query", {}).get("pages", []), key=lambda p: p.get("index", 0))
    return info(pages, width)

# Wikimedia only serves standard thumbnail widths without throttling.
STD = (500, 960, 1280, 1920, 3840)

def get(title, ident, assets, width=1920):
    q = lambda w: info(api({"action": "query", "titles": title, "prop": "imageinfo",
                            "iiprop": "url|size|mime|extmetadata", "iiurlwidth": w})["query"]["pages"], w)[0]
    it = q(width)
    # An original narrower than the asked width makes Commons serve the original, which 429s
    # every time; ask for the largest standard thumbnail below the original instead.
    if it["width"] and it["width"] <= width:
        smaller = [s for s in STD if s < it["width"]]
        if smaller:
            it = q(smaller[-1])
    ext = os.path.splitext(urllib.parse.urlparse(it["url"]).path)[1].lower() or ".jpg"
    os.makedirs(assets, exist_ok=True)
    path = os.path.join(assets, ident + ext)
    data = fetch(it["url"], timeout=60)  # fetch first: a failed download leaves no 0-byte file
    with open(path + ".part", "wb") as f:
        f.write(data)
    os.replace(path + ".part", path)
    man = os.path.join(assets, "manifest.json")
    # lock: several fetchers may write the same manifest in parallel
    import fcntl
    with open(man + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        m = json.load(open(man)) if os.path.exists(man) else {}
        m[ident] = {"file": os.path.basename(path), **{k: it[k] for k in ("title", "page", "license", "artist")}}
        tmp = man + ".tmp"
        json.dump(m, open(tmp, "w"), indent=2)
        os.replace(tmp, man)
    print(f"{ident}: {path} [{it['license']}]")

if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[a.index("--n") + 1]) if "--n" in a else 8
    w = int(a[a.index("--width") + 1]) if "--width" in a else 1920
    w = min(STD, key=lambda s: abs(s - w))
    if a[0] == "search":
        for r in search(a[1], n, w, "drawing" if "--drawing" in a else "bitmap"):
            print(f"{r['title']} | {r['width']}x{r['height']} | {r['license']}")
    elif a[0] == "get":
        get(a[1], a[2], a[3], w)
