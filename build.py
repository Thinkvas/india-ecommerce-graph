"""Build the page: inject data/webdata.json, data/india_states.geo.json and data/kgraph.json into src/graph.src.html.
Outputs: index.html (GitHub Pages; flow diagram off), dist/artifact.html (claude.ai artifact body), Desktop copy.
All non-ASCII characters are escaped so the page renders correctly whatever charset the host assumes."""
import re
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"


def js_esc(s):
    out = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch)
        else:
            b = ch.encode("utf-16-be")
            out.extend("\\u%02x%02x" % (b[i], b[i + 1]) for i in range(0, len(b), 2))
    return "".join(out)


def html_esc(s):
    return "".join(ch if ord(ch) < 128 else "&#x%x;" % ord(ch) for ch in s)


def css_esc(s):
    return "".join(ch if ord(ch) < 128 else "\\%x " % ord(ch) for ch in s)


page = (HERE / "src" / "graph.src.html").read_text()
for tag, f in [("WEBDATA", "webdata.json"), ("GEODATA", "india_states.geo.json"), ("KGRAPH", "kgraph.json")]:
    blob = (DATA / f).read_text().replace("</", "<\\/")
    page, n = re.subn(r"/\*%s\*/.*?/\*END\*/" % tag, lambda _: "/*%s*/" % tag + blob + "/*END*/", page, count=1, flags=re.S)
    assert n == 1, tag + " marker not found"

parts = re.split(r"(<script>.*?</script>|<style>.*?</style>)", page, flags=re.S)
page = "".join(js_esc(p) if p.startswith("<script>") else css_esc(p) if p.startswith("<style>") else html_esc(p) for p in parts)
page = '<meta charset="utf-8">\n' + page
assert all(ord(c) < 128 for c in page), "non-ASCII left"
(HERE / "dist").mkdir(exist_ok=True)
(HERE / "dist" / "artifact.html").write_text(page)

head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style>\n'
        '</head>\n<body>\n')
full = head + page + "\n</body>\n</html>\n"
Path("/Users/macbook/Desktop/India_Ecommerce_Knowledge_Graph.html").write_text(full)
FLOW = 'function flowActive(){ return view==="net"&&!!month&&(!selected||byId.get(selected).type==="state"); }'
assert FLOW in full
(HERE / "index.html").write_text(full.replace(FLOW, 'function flowActive(){ return false; }   // previous version: no flow diagram'))
print("built", len(page), "bytes, ASCII-only")
