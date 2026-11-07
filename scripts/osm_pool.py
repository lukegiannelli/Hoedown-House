#!/usr/bin/env python3
"""List every billiards/pool place OpenStreetMap knows about in the Hoedown House radius (prints JSON lines).
Discovery only: a human/Claude verifies each one before it goes into pool.json."""
import json, urllib.parse, urllib.request
BBOX = "31.9,-98.6,33.95,-95.3"   # S,W,N,E: greater DFW out to Denton, Waco edge, Sherman, Tyler edge
Q = f"""[out:json][timeout:120];
(
  nwr["sport"~"billiards|pool|snooker|8pool|9pool",i]({BBOX});
  nwr["leisure"="sports_hall"]["sport"~"billiards",i]({BBOX});
  nwr["name"~"billiard|pool hall|cue club|snooker|8 ball|eight ball",i]({BBOX});
);
out center tags;"""
req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": Q}).encode(),
                             headers={"User-Agent": "hoedown-house/1.0 (https://github.com/lukegiannelli/Hoedown-House)"})
els = json.load(urllib.request.urlopen(req, timeout=180))["elements"]
seen = set()
for e in els:
    t = e.get("tags", {})
    name = t.get("name")
    if not name: continue
    lat = e.get("lat") or e.get("center", {}).get("lat"); lon = e.get("lon") or e.get("center", {}).get("lon")
    k = (name.lower(), round(lat, 3), round(lon, 3))
    if k in seen: continue
    seen.add(k)
    addr = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
    print("CAND", json.dumps({"n": name, "lat": round(lat, 5), "lon": round(lon, 5), "a": addr, "city": t.get("addr:city", ""),
                              "amenity": t.get("amenity", ""), "leisure": t.get("leisure", ""), "sport": t.get("sport", ""),
                              "shop": t.get("shop", ""), "web": t.get("website", "")}, ensure_ascii=False))
print("TOTAL", len(seen))
