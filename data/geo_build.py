"""Datameet state boundaries (Admin2.shp) -> small GeoJSON with our state ids, for the 3D map view.
Source: https://github.com/datameet/maps (States/Admin2), credit Datameet."""
import json
import sys
from pathlib import Path

import shapefile
from shapely.geometry import mapping, shape

SRC = Path(sys.argv[1])          # folder holding Admin2.shp/.dbf/.shx
OUT = Path(__file__).parent / "india_states.geo.json"
NAME2ID = {
    "Andhra Pradesh": "ap", "Rajasthan": "rajasthan", "Assam": "assam", "Haryana": "haryana", "Chhattisgarh": "cg",
    "Dadra and Nagar Haveli and Daman and Diu": "dnhdd", "Gujarat": "gujarat", "Jammu & Kashmir": "jk", "Kerala": "kerala",
    "Lakshadweep": "lakshadweep", "Maharashtra": "maharashtra", "Ladakh": "ladakh", "Goa": "goa", "Telangana": "telangana",
    "Andaman & Nicobar": "andaman", "Delhi": "delhi", "Odisha": "odisha", "Himachal Pradesh": "hp", "Meghalaya": "meghalaya",
    "Jharkhand": "jharkhand", "Sikkim": "sikkim", "Puducherry": "puducherry", "Arunachal Pradesh": "arunachal",
    "Uttarakhand": "uttarakhand", "West Bengal": "wb", "Karnataka": "karnataka", "Manipur": "manipur", "Uttar Pradesh": "up",
    "Tamil Nadu": "tn", "Mizoram": "mizoram", "Punjab": "punjab", "Nagaland": "nagaland", "Madhya Pradesh": "mp",
    "Tripura": "tripura", "Chandigarh": "chandigarh", "Bihar": "bihar"}
TINY = {"delhi", "chandigarh", "goa", "puducherry", "dnhdd", "lakshadweep", "sikkim", "tripura"}


def rnd(c):
    if isinstance(c[0], (int, float)):
        return [round(c[0], 3), round(c[1], 3)]
    return [rnd(x) for x in c]


r = shapefile.Reader(str(SRC / "Admin2"))
feats, seen = [], set()
for sr in r.iterShapeRecords():
    name = sr.record["ST_NM"].strip()
    sid = NAME2ID[name]
    geom = shape(sr.shape.__geo_interface__)
    tol = 0.004 if sid in TINY else 0.03                    # keep small UTs recognisable
    simple = geom.simplify(tol, preserve_topology=True)
    if simple.geom_type == "MultiPolygon":                  # drop specks (tiny islands) except for island UTs
        keep = [p for p in simple.geoms if p.area > (0 if sid in {"andaman", "lakshadweep", "dnhdd", "puducherry"} else 0.004)]
        from shapely.geometry import MultiPolygon
        simple = MultiPolygon(keep) if len(keep) > 1 else keep[0]
    c = geom.representative_point()
    g = mapping(simple)
    feats.append({"type": "Feature", "properties": {"id": sid, "c": [round(c.x, 3), round(c.y, 3)]},
                  "geometry": {"type": g["type"], "coordinates": rnd(g["coordinates"])}})
    seen.add(sid)
missing = set(NAME2ID.values()) - seen
assert not missing, missing
OUT.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")))
print(len(feats), "states,", OUT.stat().st_size, "bytes")
