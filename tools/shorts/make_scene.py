#!/usr/bin/env python3
"""Build a Picsart Media Studio scene for a Safe House Church vertical short.

Usage:
  python3 make_scene.py config.json out_scene.json

config.json:
{
  "video": "https://...mp4",          # trimmed 1920x1080 clip (already cut to the moment)
  "duration": 67.3667,                 # clip length in seconds (multiple of 1/30)
  "words": [{"text": "But", "start": 0.09, "end": 0.23}, ...],  # word timings relative to clip start
  "title1": "NOT SHUT OUT.",           # white headline line (short, ALL CAPS)
  "title2": "SHUT IN.",                # gold headline line (short, ALL CAPS)
  "footer1": "From Sunday's message: Faithfulness",
  "footer2": "Pastor Matthew Hughes  ·  @SafeHousePHX",
  "music": "https://safehousechurch.org/media/music/<track>.mp3",  # omit for voice only
  "music_volume": 14
}
"""
import json, sys

cfg = json.load(open(sys.argv[1]))
D = round(round(cfg["duration"] * 30) / 30, 4)
FIX = {"god": "God", "jesus": "Jesus", "bible": "Bible", "lord": "Lord", "i": "I"}


def clean(t):
    t = t.strip()
    low = t.lower().strip(".,!?")
    if low in FIX:
        t = t.lower().replace(low, FIX[low], 1)
    if t.lower().startswith("i'"):
        t = "I" + t[1:]
    return t.upper()


words = []
for w in cfg["words"]:
    s, e = float(w["start"]), float(w["end"])
    if s < 0 or s >= D - 0.02:
        continue
    words.append({"text": clean(w["text"]), "start": round(s, 3), "end": round(min(e, D - 0.01), 3)})

segs, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    if len(cur) >= 3 or w["text"][-1] in ".,?!" or nxt is None or nxt["start"] - w["end"] > 0.35:
        end = nxt["start"] if (nxt and nxt["start"] - w["end"] < 0.6) else w["end"] + 0.25
        segs.append({"start": cur[0]["start"], "end": round(min(end, D - 0.01), 3),
                     "text": " ".join(x["text"] for x in cur), "words": cur})
        cur = []

mv = cfg.get("music_volume", 14)
fade_out_start = max(D - 3.4, 2.5)
scene = {
    "version": "1.0",
    "composition": {"width": 1080, "height": 1920, "fps": 30, "duration": D, "background": "#141414"},
    "assets": {
        "svc": {"type": "video", "uri": cfg["video"]},
        "logo": {"type": "image", "uri": "https://safehousechurch.org/images/logo-transparent.png", "width": 352, "height": 273},
        "music": {"type": "audio", "uri": cfg.get("music") or ""},
        "mblack": {"type": "font", "name": "Montserrat Black", "uri": "https://pastatic.picsart.com/68457958041436093893.ttf"},
        "mbold": {"type": "font", "name": "Montserrat Bold", "uri": "https://pastatic.picsart.com/99196933912641114096.ttf"},
    },
    "layers": [
        {"id": "bg", "start": 0, "duration": D,
         "content": {"kind": "media", "assetId": "svc", "fit": "cover", "muted": True},
         "effects": [{"id": "gaussian_blur", "params": {"blur": 45}}]},
        {"id": "dim", "start": 0, "duration": D, "content": {"kind": "color", "color": "#000000B3"}},
        {"id": "main", "start": 0, "duration": D, "transform": {"position": [540, 1000]},
         "content": {"kind": "media", "assetId": "svc", "fit": "cover", "bounds": [1080, 1080], "align": "center", "volume": 100}},
        {"id": "logo", "start": 0, "duration": D, "transform": {"position": [540, 165]},
         "content": {"kind": "media", "assetId": "logo", "fit": "contain", "bounds": [190, 150]}},
        {"id": "caps", "start": 0, "duration": D, "transform": {"position": [540, 1400]},
         "content": {"kind": "captions", "transcript": {"segments": segs},
                     "style": {"font": {"family": "mblack", "size": 58}, "color": "#FFFFFF", "alignment": "center", "wrapWidth": 900,
                               "effects": [{"id": "drop_shadow", "params": {"blur": 14, "offset": [0, 4], "color": "#000000E6"}}],
                               "decorations": [{"target": "highlighted", "place": "text", "color": "#D6A54A"}]}}},
        {"id": "title1", "start": 0, "duration": D, "transform": {"position": [540, 300]},
         "content": {"kind": "text", "text": cfg["title1"], "font": {"family": "mblack", "size": 64}, "color": "#FFFFFF", "alignment": "center"}},
        {"id": "title2", "start": 0, "duration": D, "transform": {"position": [540, 378]},
         "content": {"kind": "text", "text": cfg["title2"], "font": {"family": "mblack", "size": 64}, "color": "#D6A54A", "alignment": "center"}},
        {"id": "footer1", "start": 0, "duration": D, "transform": {"position": [540, 1590]},
         "content": {"kind": "text", "text": cfg["footer1"], "font": {"family": "mbold", "size": 32}, "color": "#D6A54A", "alignment": "center"}},
        {"id": "footer2", "start": 0, "duration": D, "transform": {"position": [540, 1638]},
         "content": {"kind": "text", "text": cfg.get("footer2", "Pastor Matthew Hughes  ·  @SafeHousePHX"), "font": {"family": "mbold", "size": 28}, "color": "#FFFFFFCC", "alignment": "center"}},
    ],
}
if not cfg.get("music"):
    # No approved music track: keep his voice only.
    scene["layers"] = [l for l in scene["layers"] if l["id"] != "music"]
    scene["assets"].pop("music", None)
if cfg.get("music"):
    # Only use real, licensed tracks from media/music/ (see tools/shorts/README.md). Never generated beds.
    scene["assets"]["music"] = {"type": "audio", "uri": cfg["music"]}
    fade_in = 1.5
    scene["layers"].append({"id": "music", "start": 0, "duration": D,
        "content": {"kind": "audio", "assetId": "music", "trim": {"in": cfg.get("music_start", 0), "out": cfg.get("music_start", 0) + D}, "volume": mv},
        "animations": {"volume": {"keyframes": [
            {"time": 0, "value": 0}, {"time": fade_in, "value": mv},
            {"time": round(fade_out_start, 3), "value": mv}, {"time": round(D - 0.2, 3), "value": 0}]}}})
json.dump(scene, open(sys.argv[2], "w"))
print(f"ok: {len(segs)} caption chunks, duration {D}s")
