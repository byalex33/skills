#!/usr/bin/env python3
"""Build a Hyperframes composition (index.html) for a bold-caps explainer video.

usage: build.py <video_dir> <hf_project_dir>

<video_dir> holds:
  beats.json            the edit (see SKILL.md / references/beats-format.md)
  audio/narration.mp3   voiceover
  audio/transcript.json word timings from `hyperframes transcribe`
  assets/               images named in beats.json (id -> assets/<id>.<ext>)

Writes <hf_project_dir>/index.html and copies assets + audio into it.
Prints a timing table and exits non-zero if any beat cannot be placed.
"""
import difflib, glob, html, json, os, re, shutil, sys

W, H = 1920, 1080
TAIL = 0.6  # seconds held after the last word

# ---------------------------------------------------------------- alignment
def norm_tokens(text):
    """Lowercase word tokens; numbers keep digits only (20,000 -> 20000)."""
    out = []
    for raw in text.split():
        t = raw.lower().replace("’", "'")
        t = re.sub(r"(?<=\d)[,.](?=\d)", "", t)
        t = re.sub(r"[^a-z0-9']", "", t)
        if t:
            out.append(t)
    return out

def align(beats, words):
    """Return the start time of every beat.

    Script tokens are matched to ASR tokens as sequences (difflib), so names
    the ASR mangles are carried by their matched neighbours; unmatched script
    tokens get times interpolated between the nearest matched ones.
    """
    script, owner = [], []
    for i, b in enumerate(beats):
        toks = norm_tokens(b["say"])
        if not toks:
            sys.exit(f"beat {i} has no words in 'say'")
        script += toks
        owner += [i] * len(toks)
    asr = [norm_tokens(w["text"]) for w in words]
    asr_flat, asr_idx = [], []
    for j, toks in enumerate(asr):
        for t in toks:
            asr_flat.append(t)
            asr_idx.append(j)
    times = [None] * len(script)
    sm = difflib.SequenceMatcher(None, script, asr_flat, autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            times[a + k] = words[asr_idx[b + k]]["start"]
    end = words[-1]["end"]
    # interpolate gaps
    known = [i for i, t in enumerate(times) if t is not None]
    if not known:
        sys.exit("alignment failed: no script word matched the transcript")
    for i in range(len(times)):
        if times[i] is None:
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            t0 = times[prev] if prev is not None else 0.0
            t1 = times[nxt] if nxt is not None else end
            i0 = prev if prev is not None else -1
            i1 = nxt if nxt is not None else len(times)
            times[i] = t0 + (t1 - t0) * (i - i0) / (i1 - i0)
    starts = []
    for i in range(len(beats)):
        starts.append(times[owner.index(i)])
    starts[0] = 0.0
    matched = len(known) / len(script)
    for i in range(1, len(starts)):
        if starts[i] <= starts[i - 1]:
            sys.exit(f"alignment not increasing at beat {i}: {beats[i]['say']!r}")
    return starts, end + TAIL, matched

# ---------------------------------------------------------------- rendering
def esc(s):
    return html.escape(s, quote=True)

def rich(text):
    """{red:WORD} {green:$5} {big:2011} {big red:42} -> word spans (class "w"), upper-cased.
    Each plain word and each emphasis group is one span so the motion layer can stagger them."""
    units, pos = [], 0
    def plain(chunk):
        units.extend(f'<span class="w">{esc(t.upper())}</span>' for t in chunk.split())
    for m in re.finditer(r"\{((?:red|green|big|small)(?: (?:red|green|big|small))*):([^}]*)\}", text):
        plain(text[pos:m.start()])
        units.append(f'<span class="w {m.group(1)}">{esc(m.group(2).upper())}</span>')
        pos = m.end()
    plain(text[pos:])
    return " ".join(units)

def lines(value):
    return value if isinstance(value, list) else [value]

# Allo Black caps average ~0.68em per character; usable widths per text class.
FIT_W = {"card-text": (132, 1700), "side-text": (96, 820)}

def _line_em(line):
    """Estimated width of one markup line, in ems of the block's base size."""
    em, pos = 0.0, 0
    for m in re.finditer(r"\{([a-z ]+):([^}]*)\}", line):
        em += len(line[pos:m.start()]) * 0.68
        k = m.group(1).split()
        em += len(m.group(2)) * 0.68 * (1.6 if "big" in k else 0.62 if "small" in k else 1)
        pos = m.end()
    return em + len(line[pos:]) * 0.68

def text_block(value, cls):
    base, maxw = FIT_W.get(cls.split()[0], (None, None))
    def ln(l):
        # shrink a line that would overflow its column instead of letting it wrap or run off-frame
        if base and _line_em(l) * base > maxw:
            return f'<div class="ln" style="font-size:{maxw / (_line_em(l) * base):.3f}em;white-space:nowrap">{rich(l)}</div>'
        return f'<div class="ln">{rich(l)}</div>'
    inner = "".join(ln(l) for l in lines(value))
    return f'<div class="{cls}">{inner}</div>'

def _arrow_svg():
    """Curved blue arrow, left-to-right, with a filled triangular head.
    The line ends inside the head, and the head is aimed along the last visible stretch of the
    curve (chord from t=0.8), so tip and line always read as one shape. pathLength=1 for draw-on."""
    import math
    p0, c1, c2, p1 = (20, 104), (50, 30), (140, 16), (184, 50)
    t = 0.8
    bez = lambda a, b, c, d: (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d
    q = (bez(p0[0], c1[0], c2[0], p1[0]), bez(p0[1], c1[1], c2[1], p1[1]))
    dx, dy = p1[0] - q[0], p1[1] - q[1]
    n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
    px, py = -dy, dx                       # perpendicular
    tip = (p1[0] + dx * 30, p1[1] + dy * 30)
    base = (p1[0] - dx * 10, p1[1] - dy * 10)
    half = 16
    b1 = (base[0] + px * half, base[1] + py * half)
    b2 = (base[0] - px * half, base[1] - py * half)
    f = lambda pt: f"{pt[0]:.1f} {pt[1]:.1f}"
    return ('<svg viewBox="0 0 220 120" class="arrow{cls}">'
            f'<path class="ar-line" pathLength="1" d="M{p0[0]} {p0[1]} C {c1[0]} {c1[1]}, {c2[0]} {c2[1]}, {p1[0]} {p1[1]}"/>'
            f'<path class="ar-head" d="M{f(tip)} L{f(b1)} L{f(b2)} Z"/></svg>')

ARROW_SVG = _arrow_svg()

def arrow(direction="right"):
    cls = {"right": "", "left": " flip", "down": " down", "up": " up"}.get(direction, "")
    return ARROW_SVG.replace("{cls}", cls)

class Assets:
    def __init__(self, src):
        self.src, self.used = src, {}
    def path(self, ident):
        hits = [p for p in glob.glob(os.path.join(self.src, ident + ".*")) if not p.endswith(".json")]
        if not hits:
            sys.exit(f"missing asset: {ident} (expected assets/{ident}.<ext>)")
        self.used[ident] = hits[0]
        return "assets/" + os.path.basename(hits[0])

    def emoji(self, char):
        """Emoji as a Twemoji SVG in assets/ (fetched once), so renders need no emoji font."""
        cps = "-".join(f"{ord(c):x}" for c in char if ord(c) != 0xFE0F)
        ident = f"emoji_{cps}"
        hits = glob.glob(os.path.join(self.src, ident + ".svg"))
        if not hits:
            import urllib.request
            url = f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg/{cps}.svg"
            try:
                data = urllib.request.urlopen(url, timeout=30).read()
            except Exception as e:
                sys.exit(f"could not fetch emoji {char!r} from {url}: {e}")
            open(os.path.join(self.src, ident + ".svg"), "wb").write(data)
        return self.path(ident)

def element(spec, assets, cls="el"):
    """An element is an image id, 'emoji:🤝', or {'text': ...}."""
    if isinstance(spec, dict) and "text" in spec:
        return text_block(spec["text"], "side-text")
    if isinstance(spec, str) and spec.startswith("emoji:"):
        return f'<img class="emoji" src="{assets.emoji(spec[6:])}" alt="">'
    return f'<img class="{cls}" src="{assets.path(spec)}" alt="">'

def pop(spec, assets):
    if not spec:
        return ""
    pos = "center"
    if isinstance(spec, dict):
        spec, pos = spec["emoji"], spec.get("at", "center")
    return f'<img class="pop pop-{pos}" src="{assets.emoji(spec)}" alt="">'

def scene_html(show, assets, prev_html):
    t = show["type"]
    if t == "text":
        body = text_block(show["text"], "card-text")
    elif t == "image":
        top = text_block(show["top"], "cap cap-top") if show.get("top") else ""
        bottom = text_block(show["bottom"], "cap cap-bottom") if show.get("bottom") else ""
        size = "img-m" if (top or bottom) else "img-l"
        body = (f'<div class="stack">{top}<div class="imgbox">{element(show["image"], assets, size + " m-img")}'
                f'{pop(show.get("pop"), assets)}</div>{bottom}</div>')
    elif t == "image_text":
        side = show.get("side", "left")
        txt = text_block(show["text"], "side-text")
        arr = f'<div class="arr-wrap">{arrow("right" if side == "left" else "left")}</div>' if show.get("arrow", True) else ""
        img = f'<div class="imgbox">{element(show["image"], assets, "img-s m-img")}{pop(show.get("pop"), assets)}</div>'
        col = f'<div class="txtcol">{arr}{txt}</div>'
        body = f'<div class="row">{col}{img}</div>' if side == "left" else f'<div class="row">{img}{col}</div>'
    elif t == "pair":
        mid = ""
        if show.get("connector", "arrow") == "arrow":
            mid = f'<div class="mid">{arrow("right")}</div>'
        cap = text_block(show["top"], "cap cap-top") if show.get("top") else ""
        body = (f'<div class="stack">{cap}<div class="row pair">{element(show["left"], assets, "img-p")}{mid}'
                f'{element(show["right"], assets, "img-p")}</div></div>')
    elif t == "blur_text":
        # static copy of the previous frame: strip motion markers so nothing in it animates
        under = prev_html or ""
        # (new names must not start with the old ones: the motion layer finds targets by substring)
        for a, b in (('class="w', 'class="sw'), ("m-img", "s-img"), ('class="imgbox', 'class="sbox'),
                     ("ar-line", "s-arline"), ("ar-head", "s-arhead"), ('class="pop', 'class="spop'),
                     ('class="emoji', 'class="semoji'), ("card-text", "s-cardtext"),
                     ("mk-line", "smkline"), ('class="mk-hl"', 'class="smkhl"')):
            under = under.replace(a, b)
        body = f'<div class="blurred" data-layout-ignore>{under}</div>{text_block(show["text"], "card-text over")}'
    else:
        sys.exit(f"unknown show.type: {t}")
    return body

# ---------------------------------------------------------------- motion
# A vocabulary of moves, chosen by meaning first and a seeded RNG second.
#   role  : what the beat does in the story (turn / climax / closer / hook / normal)
#           -> sets speed, easing, which moves are allowed, and the scene transition
#   seed  : random.Random("beat-<i>") picks inside the allowed set, never repeating the last pick
# A beat may force any pick: "motion": {"role": "climax", "image": "slide-left", "marker": "circle", ...}
IMG_IN = {
    "rise":        ({"opacity": 0, "y": 40, "scale": 0.92}, {"ease": "back.out(1.4)", "duration": 0.45}),
    "slide-left":  ({"opacity": 0, "x": -260}, {"ease": "power4.out", "duration": 0.5}),
    "slide-right": ({"opacity": 0, "x": 260}, {"ease": "power4.out", "duration": 0.5}),
    "zoom-out":    ({"opacity": 0, "scale": 1.3}, {"ease": "power3.out", "duration": 0.55}),
    "drop":        ({"opacity": 0, "y": -220}, {"ease": "bounce.out", "duration": 0.7}),
    "tilt":        ({"opacity": 0, "rotation": -7, "scale": 0.85}, {"ease": "back.out(1.8)", "duration": 0.5}),
    "punch":       ({"opacity": 0, "scale": 0.55}, {"ease": "elastic.out(1, 0.6)", "duration": 0.8}),
}
DRIFT = {  # per-second rates for the slow move that runs for the whole beat; "still" = no move
    "zoom-in":   {"scale": 0.02},
    "zoom-out":  {"scale": -0.02},
    "pan-left":  {"x": -14, "scale": 0.008},
    "pan-right": {"x": 14, "scale": 0.008},
    "tilt":      {"rotation": 0.5, "scale": 0.01},
    "still":     {},
}
TEXT_IN = {
    "rise":    (".w", {"opacity": 0, "y": 46}, {"ease": "power3.out", "duration": 0.38, "stagger": 0.055}),
    "drop":    (".w", {"opacity": 0, "y": -60}, {"ease": "back.out(2)", "duration": 0.45, "stagger": 0.06}),
    "pop":     (".w", {"opacity": 0, "scale": 0.3}, {"ease": "back.out(3)", "duration": 0.4, "stagger": 0.07}),
    "swing":   (".w", {"opacity": 0, "rotation": -18, "y": 30}, {"ease": "back.out(2.2)", "duration": 0.45, "stagger": 0.06}),
    "lines":   (".ln", {"opacity": 0, "x": -140}, {"ease": "power4.out", "duration": 0.45, "stagger": 0.12}),
    "zoom":    (".ln", {"opacity": 0, "scale": 2.2}, {"ease": "power4.out", "duration": 0.5, "stagger": 0.1}),
}
EMPH = {
    "punch":   ({"scale": 1.45}, {"scale": 1, "ease": "back.out(2.6)", "duration": 0.5}),
    "stretch": ({"scaleX": 1.6, "scaleY": 0.7}, {"scaleX": 1, "scaleY": 1, "ease": "elastic.out(1, 0.45)", "duration": 0.8}),
    "shake":   ({"rotation": -9}, {"rotation": 0, "ease": "elastic.out(1.2, 0.25)", "duration": 0.8}),
}
EMPH_SOFT = {  # long words: smaller moves so the word never covers its neighbours
    "hop":   ({"y": -30}, {"y": 0, "ease": "bounce.out", "duration": 0.6}),
    "shake": ({"rotation": -4}, {"rotation": 0, "ease": "elastic.out(1.2, 0.25)", "duration": 0.8}),
}
POP_IN = {
    "bounce": ({"scale": 0, "rotation": -25}, {"scale": 1, "rotation": 0, "ease": "back.out(2.6)", "duration": 0.55}),
    "spin":   ({"scale": 0.2, "rotation": -200}, {"scale": 1, "rotation": 0, "ease": "back.out(1.6)", "duration": 0.65}),
    "drop":   ({"y": -260, "opacity": 0}, {"y": 0, "opacity": 1, "ease": "bounce.out", "duration": 0.7}),
}
SCENE_IN = {  # transitions by meaning: hook -> push-up (new section), climax -> zoom-through, normal -> occasional push-left
    "push-left":    ({"x": 320, "opacity": 0}, {"ease": "power4.out", "duration": 0.4}),
    "push-up":      ({"y": 200, "opacity": 0}, {"ease": "power4.out", "duration": 0.4}),
    "zoom-through": ({"scale": 0.8, "opacity": 0}, {"ease": "expo.out", "duration": 0.35}),
}
MARKERS = ("underline", "circle", "highlight")
# role -> speed multiplier (slowest 1.5 vs fastest 0.6: 2.5x), easing override, allowed moves
ROLES = {
    "turn":   {"speed": 0.0},
    "climax": {"speed": 0.6, "ease": "expo.out", "image": ["punch", "zoom-out", "slide-left", "slide-right"],
               "text": ["zoom", "pop", "drop"], "drift": ["zoom-in", "pan-left", "pan-right"], "marker_p": 1.0},
    "closer": {"speed": 1.5, "ease": "sine.out", "image": ["rise", "zoom-out", "slide-left", "slide-right"],
               "text": ["rise", "lines"], "drift": ["zoom-in", "zoom-out", "pan-left", "pan-right", "still"],
               "drift_rate": 0.6, "marker_p": 0.5},
    "hook":   {"speed": 0.9, "marker_p": 0.35},
    "normal": {"speed": 1.0, "marker_p": 0.35},
}
COUNT_RE = re.compile(r"^(\$?)(\d{1,3}(?:,\d{3})+)$")   # 20,000  $500,000 — not years
MONTHS = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
EMPH_SPAN = re.compile(r'<span class="w ([a-z ]*(?:red|green|big)[a-z ]*)">([^<]+)</span>')

def beat_role(b, next_b):
    """What this beat does in the story. Closer > turn > climax > hook > normal."""
    if b.get("show", {}).get("motion", {}).get("role"):
        return b["show"]["motion"]["role"]
    say = b["say"].strip().lower()
    if next_b is None or next_b["show"]["type"] == "lineup":
        return "closer"
    if re.match(r"^(but|however|yet|instead|then|until|except)\b", say):
        return "turn"
    # climax = a full date or a big figure: rare by design (about one or two per chapter)
    if (re.search(MONTHS + r"[^a-z]{0,6}\d{4}", say) or re.search(r"\d{4}[^a-z]{0,4}" + MONTHS, say)
            or re.search(r"\b\d{1,3}(,\d{3})+\b", say)):
        return "climax"
    if b["_bi"] == 1:
        return "hook"
    return "normal"

def pick(rng, table, avoid, forced=None, weights=None, allowed=None):
    if forced:
        if forced not in table:
            sys.exit(f"unknown motion {forced!r}; choose from {list(table)}")
        return forced
    keys = [k for k in (allowed or table) if k in table]
    keys = [k for k in keys if k != avoid] or keys
    w = [weights.get(k, 1) for k in keys] if weights else None
    return rng.choices(keys, weights=w)[0]

def add_marker(html_body, kind):
    """Draw a marker on the first emphasis word that does not count up. Returns (html, applied)."""
    for m in EMPH_SPAN.finditer(html_body):
        # a circle only reads round on a short word; on long or big text it balloons off-frame
        limit = (8 if "big" in m.group(1) else 12) if kind == "circle" else 16
        if len(m.group(2)) > limit:
            continue
        word = f'<span class="mk-t">{m.group(2)}</span>'   # count-up writes into .mk-t, keeping the marker
        if kind == "highlight":
            inner = f'<span class="mk-hl"></span>{word}'
        elif kind == "underline":
            inner = (f'{word}<svg class="mk mk-under" viewBox="0 0 100 10" preserveAspectRatio="none">'
                     '<path class="mk-line" pathLength="1" d="M2 6 C 25 2, 50 9, 75 4 S 95 5, 98 3"/></svg>')
        else:
            inner = (f'{word}<svg class="mk mk-circle" viewBox="0 0 100 50" preserveAspectRatio="none">'
                     '<path class="mk-line" pathLength="1" d="M60 4 C 90 2, 99 18, 97 28 C 94 44, 60 48, 40 47 '
                     'C 15 46, 2 36, 3 24 C 4 10, 25 3, 55 5 C 62 5, 68 7, 72 9"/></svg>')
        span = f'<span class="w {m.group(1)} mk-host mk-{kind}-host">{inner}</span>'
        return html_body[:m.start()] + span + html_body[m.end():], True
    if kind == "circle":
        return add_marker(html_body, "underline")
    return html_body, False

def motion(i, cid, html_body, show, prev_show, t0, dur, st, role):
    """GSAP tweens for one beat. st carries the previous picks and the drift end state."""
    import random
    rng = random.Random(f"beat-{i}")
    force = show.get("motion", {})
    R = ROLES[role]
    speed = R["speed"] * (rng.uniform(0.85, 1.15) if role in ("normal", "hook") else 1.0)
    turn = role == "turn"
    js, picks = [], {"role": role}
    def add(target, frm, to, at=0.0):
        js.append(f'tl.fromTo("#{cid} {target}",{json.dumps(frm)},{json.dumps(to)},{t0 + at:.3f});')
    def timed(opts, keep_ease=False):
        o = dict(opts)
        o["duration"] = round(o["duration"] * speed, 3)
        if "stagger" in o:
            o["stagger"] = round(o["stagger"] * speed, 3)
        if R.get("ease") and not keep_ease:
            o["ease"] = R["ease"]
        return o
    def entrance(target, spec, at=0.0, keep_ease=False):
        frm, opts = spec
        to = {k: (1 if k in ("opacity", "scale") else 0) for k in frm}
        to.update(timed(opts, keep_ease))
        add(target, frm, to, at)
    has = lambda marker: marker in html_body
    same_img = bool(prev_show and show.get("image") and prev_show.get("image") == show.get("image")
                    and prev_show.get("type") in ("image", "image_text") and show["type"] in ("image", "image_text"))

    # scene transition, by meaning; a turn is a hard cut with a small jolt
    picks["scene"] = "none"
    if turn:
        add(".scene", {"scale": 1.06}, {"scale": 1, "duration": 0.18, "ease": "expo.out"})
        picks["scene"] = "hard-cut"
    elif not same_img:
        scene = force.get("scene")
        if not scene:
            if role == "hook":
                scene = "push-up"
            elif role == "climax":
                scene = "zoom-through"
            elif role == "normal" and st.get("scene") in (None, "none") and rng.random() < 0.18:
                scene = "push-left"
        if scene:
            picks["scene"] = pick(rng, SCENE_IN, None, scene)
            entrance(".scene", SCENE_IN[scene], keep_ease=True)
    lead = 0.0 if turn else (0.08 if picks["scene"] != "none" else 0.1)  # first move 0.1 s in: no jump-cut feel

    if has("m-img") and not same_img and not turn:
        picks["image"] = pick(rng, IMG_IN, st.get("image"), force.get("image"), allowed=R.get("image"))
        entrance(".m-img", IMG_IN[picks["image"]], lead, keep_ease=picks["image"] == "punch")
    if has('class="imgbox'):
        if same_img and st.get("drift"):
            picks["drift"], start = st["drift"], dict(st["drift_end"])
        else:
            allowed = ["still"] if turn else R.get("drift")
            picks["drift"] = pick(rng, DRIFT, st.get("drift"), force.get("drift"), allowed=allowed,
                                  weights={"still": 0.5})
            start = {"scale": 1.06 if picks["drift"] == "zoom-out" else 1.0, "x": 0, "rotation": 0}
        rate = {k: v * R.get("drift_rate", 1.0) for k, v in DRIFT[picks["drift"]].items()}
        end = {k: round(start.get(k, 0) + rate.get(k, 0) * dur, 4) for k in ("scale", "x", "rotation")}
        end["scale"] = max(0.96, min(end["scale"], 1.15)); end["x"] = max(-90, min(end["x"], 90))
        if picks["drift"] != "still":
            add(".imgbox", start, {**end, "duration": round(dur, 3), "ease": "none"})
        st["drift_end"] = end
    if has('class="w') and not turn:
        picks["text"] = pick(rng, TEXT_IN, st.get("text"), force.get("text"), allowed=R.get("text"),
                             weights={"zoom": 2, "pop": 1.5} if show["type"] == "text" else {"zoom": 0.3})
        target, frm, opts = TEXT_IN[picks["text"]]
        start = lead + (0.0 if show["type"] in ("text", "blur_text") else 0.14 * speed)
        emph_words = [m.group(2) for m in EMPH_SPAN.finditer(html_body)] + \
                     re.findall(r'mk-host[^"]*">(?:<span class="mk-hl"></span>)?<span class="mk-t">([^<]+)<', html_body)
        emph_table = None
        if emph_words:
            short = max(len(w) for w in emph_words) <= 6
            emph_table = EMPH if short else EMPH_SOFT
            picks["emph"] = pick(rng, emph_table, st.get("emph"), force.get("emph"))
        efrm, eto = emph_table[picks["emph"]] if emph_table else (None, None)
        EMPH_SEL = ".w.red, .w.green, .w.big"
        if target == ".w" and emph_table:
            # importance first: the key word lands, then the rest follows; total stagger ≤ 0.5 s
            others = ".w:not(.red):not(.green):not(.big)"
            n = len(re.findall(r'class="w"', html_body))
            o = timed(opts); o["stagger"] = round(min(o["stagger"], 0.5 / max(n - 1, 1)), 3)
            add(EMPH_SEL, {**efrm, "opacity": 0}, {**eto, "opacity": 1, "duration": round(eto["duration"] * speed, 3)}, start)
            to = {k: (1 if k in ("opacity", "scale") else 0) for k in frm}; to.update(o)
            add(others, frm, to, start + 0.12 * speed)
        else:
            n = len(re.findall(r'class="ln"', html_body)) if target == ".ln" else len(re.findall(r'class="w', html_body))
            o = timed(opts); o["stagger"] = round(min(o["stagger"], 0.5 / max(n - 1, 1)), 3)
            to = {k: (1 if k in ("opacity", "scale") else 0) for k in frm}; to.update(o)
            add(target, frm, to, start)
            if emph_table:
                add(EMPH_SEL, efrm, {**eto, "duration": round(eto["duration"] * speed, 3)}, start + 0.22 * speed)
    # count-up for big figures (also on turns: the number still matters)
    for k, m in enumerate(re.finditer(r'<span class="w([^"]*)">(?:<span class="mk-hl"></span>)?(?:<span class="mk-t">)?([^<]+)<', html_body)):
        cm = COUNT_RE.match(m.group(2))
        if cm:
            n = int(cm.group(2).replace(",", ""))
            js.append(f'countUp("{cid}", {k}, "{cm.group(1)}", {n}, {t0 + lead + 0.1:.3f});')
    # marker on the key word, drawn after the word has landed
    mk_at = lead + (0.2 if turn else 0.4 * max(speed, 0.6))
    if has("mk-line"):
        dur_mk = 0.6 if has("mk-circle") else 0.45
        add(".mk-line", {"strokeDashoffset": 1}, {"strokeDashoffset": 0, "duration": round(dur_mk * max(speed, 0.6), 3),
                                                  "ease": "power2.inOut"}, mk_at)
    if has('class="mk-hl"'):
        add(".mk-hl", {"scaleX": 0}, {"scaleX": 1, "duration": round(0.35 * max(speed, 0.6), 3), "ease": "power3.out"}, mk_at)
    if has("card-text") and show["type"] == "text" and not turn:
        add(".card-text", {"scale": 1}, {"scale": 1.045, "duration": round(dur, 3), "ease": "none"})
    if has("ar-line"):
        sp = max(speed, 0.6)
        add(".ar-line", {"strokeDashoffset": 1}, {"strokeDashoffset": 0, "duration": round(0.42 * sp, 3), "ease": "power2.inOut"}, lead + 0.12)
        add(".ar-head", {"opacity": 0, "scale": 0.4}, {"opacity": 1, "scale": 1, "duration": 0.2, "ease": "back.out(3)",
                                                       "transformOrigin": "50% 50%"}, lead + 0.12 + 0.36 * sp)
    if has('class="pop') or has('class="emoji'):
        picks["pop"] = pick(rng, POP_IN, st.get("pop"), force.get("pop"))
        sp_save = speed; speed = max(speed, 0.6)
        if has('class="pop'):
            entrance(".pop", POP_IN[picks["pop"]], lead + 0.3 * speed, keep_ease=True)
        if has('class="emoji'):
            entrance(".emoji", POP_IN[picks["pop"]], lead + 0.15 * speed, keep_ease=True)
        speed = sp_save
    if show["type"] == "pair" and not turn:
        style = pick(rng, {"slide": 1, "pop": 1, "drop": 1}, st.get("pair"), force.get("pair"))
        picks["pair"] = style
        d = lambda x: round(x * speed, 3)
        if style == "slide":
            add(".pair > :first-child", {"x": -160, "opacity": 0}, {"x": 0, "opacity": 1, "duration": d(0.45), "ease": R.get("ease", "power3.out")}, lead)
            add(".pair > :last-child", {"x": 160, "opacity": 0}, {"x": 0, "opacity": 1, "duration": d(0.45), "ease": R.get("ease", "power3.out")}, lead + d(0.35))
        elif style == "pop":
            add(".pair > :first-child", {"scale": 0.5, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": d(0.5), "ease": R.get("ease", "back.out(2)")}, lead)
            add(".pair > :last-child", {"scale": 0.5, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": d(0.5), "ease": R.get("ease", "back.out(2)")}, lead + d(0.4))
        else:
            add(".pair > :first-child", {"y": -200, "opacity": 0}, {"y": 0, "opacity": 1, "duration": d(0.6), "ease": "bounce.out"}, lead)
            add(".pair > :last-child", {"y": 200, "opacity": 0}, {"y": 0, "opacity": 1, "duration": d(0.6), "ease": "bounce.out"}, lead + d(0.35))
        add(".pair", {"scale": 1}, {"scale": 1.025, "duration": round(dur, 3), "ease": "none"})
    if has("blurred") and not turn:
        add(".blurred", {"opacity": 0, "scale": 1.15}, {"opacity": 0.85, "scale": 1, "duration": round(0.45 * speed, 3), "ease": "power2.out"})
    for k in ("scene", "image", "drift", "text", "emph", "pop", "pair"):
        if k in picks:
            st[k] = picks[k]
    return js, picks

COUNT_UP_JS = """
function countUp(cid, idx, prefix, n, at) {
  const host = document.querySelectorAll('#' + cid + ' .w')[idx];
  if (!host) return;
  const el = host.querySelector('.mk-t') || host;
  el.style.minWidth = el.getBoundingClientRect().width + 'px';
  el.style.fontVariantNumeric = 'tabular-nums';
  const o = { v: 0 };
  const fmt = v => prefix + Math.round(v).toLocaleString('en-US');
  tl.fromTo(o, { v: 0 }, { v: n, duration: 0.9, ease: 'power2.out',
    onUpdate: () => { el.textContent = fmt(o.v); } }, at);
}
"""

def lineup_html(items, assets):
    n = len(items)
    cols = n if n <= 4 else (n + 1) // 2
    rows = 1 if n <= 4 else 2
    cw, ch = W / cols, (H / rows if rows == 2 else H * 0.6)
    oy = 0 if rows == 2 else (H - ch) / 2
    cells, centers = [], {}
    for k, it in enumerate(items):
        c, r = k % cols, k // cols
        x, y = c * cw, oy + r * ch
        centers[it["id"]] = (x + cw / 2, y + ch / 2, cw, r)
        # cap image height by cell width so tall images still fit the frame when zoomed
        img_h = min(ch * 0.62, cw * 0.42)
        cells.append(
            f'<div class="lu-cell" style="left:{x:.0f}px;top:{y:.0f}px;width:{cw:.0f}px;height:{ch:.0f}px">'
            f'<img src="{assets.path(it["image"])}" alt="" style="max-height:{img_h:.0f}px">'
            f'<div class="lu-label" data-layout-ignore>{esc(it["label"])}</div></div>')
    return "".join(cells), centers

def lineup_target(center, shift_cells=0):
    """GSAP x/y/scale that frames one lineup cell; shift_cells offsets the view sideways."""
    cx, cy, cw, _ = center
    s = W / cw * 0.92
    return {"x": W / 2 - s * (cx + shift_cells * cw), "y": H / 2 - s * cy, "scale": s}

def lineup_source(centers, prev_item, item):
    """Where a lineup move starts: the previous item when it is on the same row (sideways pan),
    else the full grid (first chapter, and row changes, which would pan diagonally through blank space)."""
    if prev_item and centers[prev_item][3] == centers[item][3]:
        return lineup_target(centers[prev_item])
    return {"x": 0, "y": 0, "scale": 1}

# Allo (SIL OFL 1.1, github.com/joshpuckett/allo), bundled in the skill's assets/fonts and copied
# into each project, so renders never depend on a font CDN or an installed font.
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
FONT_FILES = {700: "Allo-Bold.woff2", 800: "Allo-ExtraBold.woff2", 900: "Allo-Black.woff2"}
FONT_FACE = "".join(
    f"@font-face{{font-family:'Allo';src:url('assets/fonts/{f}') format('woff2');font-weight:{w};font-style:normal;font-display:block}}\n"
    for w, f in FONT_FILES.items())

CSS = FONT_FACE + """
:root{--ink:#0b0b0b;--red:#e01b1b;--green:#19b23b;--blue:#1d8fe1;--ground:#ffffff;
--font:'Allo',system-ui,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:var(--ground)}
#root{position:relative;width:1920px;height:1080px;background:var(--ground);font-family:var(--font);color:var(--ink)}
.clip img:not(.pop):not(.emoji){mix-blend-mode:multiply}
.clip{position:absolute;inset:0;width:1920px;height:1080px;background:var(--ground);overflow:hidden}
.chap{position:absolute;left:16px;top:10px;font-weight:800;font-size:22px;letter-spacing:.02em;z-index:5}
.scene{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.ln{line-height:.98;text-transform:uppercase}
.red{color:var(--red)} .green{color:var(--green)} .big{font-size:1.6em} .small{font-size:.62em}
.card-text{font-weight:900;font-size:132px;text-align:center;letter-spacing:-.01em}
.card-text.over{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:2}
.cap{font-weight:900;text-align:center;font-size:62px;max-width:1700px}
.cap-top{margin-bottom:22px} .cap-bottom{margin-top:22px}
.stack{display:flex;flex-direction:column;align-items:center;justify-content:center}
.imgbox{position:relative;display:inline-block}
.img-l{max-width:1250px;max-height:860px;display:block}
.img-m{max-width:1150px;max-height:720px;display:block}
.img-s{max-width:880px;max-height:800px;display:block}
.img-p{max-width:640px;max-height:600px;display:block}
.emoji{width:300px;height:300px;display:block}
.row{display:flex;align-items:center;justify-content:center;gap:56px}
.txtcol{display:flex;flex-direction:column;align-items:center;max-width:820px}
.side-text{font-weight:900;font-size:96px;text-align:center}
.arr-wrap{align-self:flex-end;margin-right:-40px;margin-bottom:8px}
.arrow{width:230px;height:126px;display:block;overflow:visible}
.arrow path{fill:none;stroke:var(--blue);stroke-width:13;stroke-linecap:round;stroke-linejoin:round}
.ar-line{stroke-dasharray:1 1}
.arrow .ar-head{fill:var(--blue);stroke-width:7}
.sbox{position:relative;display:inline-block} .sw{display:inline-block}
.s-cardtext{font-weight:900;font-size:132px;text-align:center}
.arrow .s-arhead{fill:var(--blue);stroke-width:7}
.spop{position:absolute;width:230px;height:230px} .semoji{width:300px;height:300px;display:block}
.w{display:inline-block}
.mk-host{position:relative;isolation:isolate}
.mk{position:absolute;overflow:visible;pointer-events:none}
.mk path{fill:none;stroke:var(--blue);stroke-linecap:round;stroke-linejoin:round}
.mk-line{stroke-dasharray:1 1}
.mk-under{left:-4%;width:108%;bottom:-.2em;height:.24em}
.mk-under path{stroke-width:3.2}
.mk-circle{left:-7%;width:114%;top:-12%;height:124%}
.mk-circle-host{margin:0 .22em}
.mk-circle path{stroke-width:2.2}
.mk-hl,.smkhl{position:absolute;left:-4%;right:-4%;top:14%;bottom:4%;background:#ffd84d;z-index:0;transform-origin:0 50%;border-radius:.08em}
.mk-t{position:relative;z-index:1}
.imgbox,.card-text,.pair{will-change:transform}
.arrow.flip{transform:scaleX(-1)} .arrow.down{transform:rotate(90deg)} .arrow.up{transform:rotate(-90deg)}
.mid .arrow{width:300px;height:164px}
.pop{position:absolute;width:230px;height:230px;z-index:3}
.pop-center{left:50%;top:50%;transform:translate(-50%,-50%)}
.pop-top-right{right:-70px;top:-70px;width:170px;height:170px}
.pop-top{left:50%;top:-60px;transform:translateX(-50%);width:170px;height:170px}
.blurred{position:absolute;inset:0;filter:blur(38px);opacity:.85}
.blurred .scene{position:absolute;inset:0}
.lu{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;background:#fff}
.lu-cell{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 18px}
.lu-cell img{max-width:100%;max-height:62%;display:block}
.lu-label{font-family:var(--font);font-weight:700;font-size:30px;margin-top:14px;text-align:center;letter-spacing:-.01em}
"""

def build(video_dir, out_dir):
    spec = json.load(open(os.path.join(video_dir, "beats.json")))
    words = json.load(open(os.path.join(video_dir, "audio", "transcript.json")))
    import subprocess
    vo_len = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                   os.path.join(video_dir, "audio", "narration.mp3")], capture_output=True, text=True).stdout)
    assets = Assets(os.path.join(video_dir, "assets"))

    # flatten chapters -> beats, remembering chapter label
    beats = []
    for ci, ch in enumerate(spec["chapters"]):
        for bi, b in enumerate(ch["beats"]):
            beats.append({**b, "_chap": ch["label"], "_ci": ci, "_bi": bi, "_item": ch.get("item")})
    starts, end, matched = align(beats, words)
    # lead the word: each visual appears LEAD s before its first word (never within 0.3 s of the previous one)
    LEAD = 0.25
    for i in range(1, len(starts)):
        starts[i] = max(min(starts[i], starts[i - 1] + 0.3), starts[i] - LEAD)

    lu_cells, centers = lineup_html(spec["lineup"], assets)
    clips, tl_js, prev_scene, prev_item = [], [], None, None
    prev_show, mstate, motion_log = None, {}, []
    for i, b in enumerate(beats):
        t0 = starts[i]
        t1 = starts[i + 1] if i + 1 < len(beats) else end
        dur = t1 - t0
        show = b["show"]
        cid = f"b{i:03d}"
        label = "" if show["type"] == "lineup" else f'<div class="chap" data-layout-ignore>{esc(b["_chap"].upper())}</div>'
        if show["type"] == "lineup":
            item = show.get("focus") or b["_item"]
            if item not in centers:
                sys.exit(f"beat {i}: lineup focus {item!r} not in lineup ids {list(centers)}")
            tgt = lineup_target(centers[item])
            src = lineup_source(centers, prev_item, item)
            move = min(1.3, dur * 0.7)
            inner = f'<div class="lu" id="lu{i}">{lu_cells}</div>'
            tl_js.append(f'tl.set("#lu{i}",{json.dumps(src)},{t0:.3f});'
                         f'tl.to("#lu{i}",{{...{json.dumps(tgt)},duration:{move:.3f},ease:"power3.inOut"}},{t0:.3f});')
            prev_item = item
            prev_scene = None
            prev_show, mstate, motion_log = None, {}, []
        else:
            inner = f'<div class="scene">{scene_html(show, assets, prev_scene)}</div>'
            role = beat_role(b, beats[i + 1] if i + 1 < len(beats) else None)
            # marker on the key word: always on a climax, sometimes elsewhere, rarely twice running
            import random
            mrng = random.Random(f"marker-{i}")
            p_mk = ROLES[role].get("marker_p", 0.3) * (0.3 if mstate.get("marker") and role != "climax" else 1.0)
            mk_kind = show.get("motion", {}).get("marker")
            if mk_kind is None and EMPH_SPAN.search(inner) and mrng.random() < p_mk:
                mk_kind = mrng.choice([m for m in MARKERS if m != mstate.get("marker_kind")])
            applied = False
            if mk_kind and mk_kind != "none":
                if mk_kind not in MARKERS:
                    sys.exit(f"beat {i}: unknown marker {mk_kind!r}; choose from {MARKERS}")
                inner, applied = add_marker(inner, mk_kind)
            mstate["marker"] = applied
            if applied:
                mstate["marker_kind"] = mk_kind
            js, picks = motion(i, cid, inner, show, prev_show, t0, dur, mstate, role)
            if applied:
                picks["marker"] = mk_kind
            b["_motion"] = picks
            tl_js.extend(js)
            prev_scene = inner
            prev_show = show
        clips.append(f'<div id="{cid}" class="clip" data-start="{t0:.3f}" data-duration="{dur:.3f}" '
                     f'data-track-index="0">{label}{inner}</div>')
        b["_t0"], b["_dur"] = t0, dur

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{end:.3f}" data-width="1920" data-height="1080">
{chr(10).join(clips)}
<audio id="vo" data-start="0" data-duration="{vo_len:.3f}" data-track-index="1" src="audio/narration.mp3"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{COUNT_UP_JS}
{chr(10).join(tl_js)}
tl.set({{}}, {{}}, {end:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    os.makedirs(os.path.join(out_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "audio"), exist_ok=True)
    for ident, p in assets.used.items():
        shutil.copy2(p, os.path.join(out_dir, "assets", os.path.basename(p)))
    shutil.copy2(os.path.join(video_dir, "audio", "narration.mp3"), os.path.join(out_dir, "audio", "narration.mp3"))
    os.makedirs(os.path.join(out_dir, "assets", "fonts"), exist_ok=True)
    for f in list(FONT_FILES.values()) + ["OFL.txt"]:
        shutil.copy2(os.path.join(FONT_DIR, f), os.path.join(out_dir, "assets", "fonts", f))
    open(os.path.join(out_dir, "index.html"), "w").write(doc)

    write_description(spec, beats, assets, video_dir)

    print(f"aligned {matched:.0%} of script words to the transcript; {len(beats)} beats; {end:.1f}s")
    for b in beats:
        mv = " ".join(f"{k}={v}" for k, v in b.get("_motion", {}).items() if v != "none")
        print(f"{b['_t0']:7.2f} {b['_dur']:5.2f}s  {b['show']['type']:<10} {b['say'][:46]:<46} {mv}")
    short = [b for b in beats if b["_dur"] < 0.35]
    if matched < 0.8:
        print("WARNING: under 80% of words matched; check the script matches the narration", file=sys.stderr)
    if short:
        print(f"WARNING: {len(short)} beats shorter than 0.35s; merge them", file=sys.stderr)

def write_description(spec, beats, assets, video_dir):
    """YouTube description: chapter timestamps, disclaimer, image credits from assets/manifest.json."""
    def mmss(t):
        t = int(t)
        return f"{t // 60}:{t % 60:02d}"
    seen, stamps = set(), []
    for b in beats:
        if b["_ci"] not in seen:
            seen.add(b["_ci"])
            stamps.append(f"{mmss(b['_t0'])} {b['_chap']}")
    man_path = os.path.join(video_dir, "assets", "manifest.json")
    man = json.load(open(man_path)) if os.path.exists(man_path) else {}
    credits = []
    for ident in sorted(assets.used):
        m = man.get(ident)
        if m:
            who = f" by {m['artist']}" if m.get("artist") else ""
            credits.append(f"- {m['title'].removeprefix('File:')}{who}, {m['license']}: {m['page']}")
    emoji = any(i.startswith("emoji_") for i in assets.used)
    text = [spec.get("title", ""), "", "TIMESTAMPS:", *stamps, "",
            "DISCLAIMER:", "This video is for general information and entertainment. Figures are approximate "
            "and sources sometimes disagree; check several reliable sources before relying on any detail.", "",
            "IMAGE CREDITS (Wikimedia Commons):", *credits]
    if emoji:
        text += ["- Emoji: Twemoji, CC BY 4.0"]
    open(os.path.join(video_dir, "description.txt"), "w").write("\n".join(text) + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
