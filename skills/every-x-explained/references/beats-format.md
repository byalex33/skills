# beats.json

```json
{
  "title": "Every WW2 Fighter Explained In 10 Minutes",
  "lineup": [
    {"id": "spitfire", "image": "lineup_spitfire", "label": "Supermarine Spitfire"}
  ],
  "chapters": [
    {"label": "Supermarine Spitfire", "item": "spitfire", "beats": [
      {"say": "Supermarine Spitfire.", "show": {"type": "lineup"}},
      {"say": "The Spitfire was designed by Reginald Mitchell,",
       "show": {"type": "image_text", "image": "mitchell", "text": ["Reginald", "Mitchell"]}}
    ]}
  ]
}
```

- `lineup`: all 8 items in display order. `image` is an asset id; `label` is printed under it.
- `chapters[].label`: chapter label top-left and the timestamp name. `item`: the lineup id this chapter zooms to.
- `say`: the exact narration words of this beat. All `say` strings joined in order = the full script. Punctuation does not matter; words do.
- Asset ids are file names in `assets/` without extension.

## `show` types

| type | fields | looks like |
|---|---|---|
| `lineup` | `focus` (optional, defaults to chapter `item`) | grid zoom/pan to the item |
| `text` | `text`: line or list of lines | caps text card |
| `image` | `image`; optional `top`, `bottom` (caption lines); optional `pop` | photo, headline above or caption below |
| `image_text` | `image`, `text`; `side`: `left` (text left, default) or `right`; `arrow`: true/false; optional `pop` | text + curved arrow beside a photo |
| `pair` | `left`, `right` (each an element); `connector`: `arrow` (default) or `none`; optional `top` | A → B |
| `blur_text` | `text` | big text over the previous frame, blurred |

**Element** (for `pair.left/right`, `image`): an asset id, `"emoji:🤝"`, or `{"text": "..."}`.

**pop**: `"✅"` or `{"emoji": "✅", "at": "center" | "top-right" | "top"}`, drawn over the image.

**motion** (optional, any non-lineup beat): force a pick instead of the seeded choice, e.g. `"motion": {"role": "climax", "image": "slide-left", "drift": "still", "text": "zoom", "emph": "shake", "marker": "circle", "pop": "spin", "pair": "drop", "scene": "push-up"}` (`"marker": "none"` turns a marker off). Names are listed in `format.md` → Motion. Use it only to fix a beat that looks wrong; let the seed choose the rest.

**Text markup** (any text field; everything is upper-cased): `{red:word}`, `{green:$500 million}`, `{big:2011}`, `{small:…}`, combined `{big red:42}`. A list makes separate lines.
