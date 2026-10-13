"""Load the researched India e-commerce data into FalkorDB (graph "india_ecom"), then export the snapshot
the web page reads (webdata.json). FalkorDB is the master copy; the page is a read-only view of it.

Graph model
  (:Region)<-[:IN_REGION]-(:State {share, culture, ecommerce, ...})-[:HAS_CITY]->(:City)
  (:Festival)-[:CELEBRATED_IN {impact, buys, reason, date_2026, date_2027, confidence}]->(:State)
  (:Festival)-[:DRIVES {impact}]->(:Product)          (:Festival)-[:IN_MONTH]->(:Month)
  (:Signal {type, direction, strength})-[:AFFECTS]->(:State)   (national signals: {national:true}, no AFFECTS)
  (:Signal)-[:LIFTS|CUTS]->(:Product)                  (:Signal)-[:IN_MONTH]->(:Month)
  (anything)-[:CITES]->(:Source {url})
"""
import json
import re
from pathlib import Path

from falkordb import FalkorDB

HERE = Path(__file__).parent
DEEP = HERE / "deep"
GRAPH = "india_ecom"
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REGION = {**{s: "north" for s in "up bihar delhi punjab haryana chandigarh hp jk ladakh uttarakhand rajasthan".split()},
          **{s: "west" for s in "maharashtra gujarat goa mp cg dnhdd".split()},
          **{s: "south" for s in "ap telangana karnataka tn kerala puducherry lakshadweep andaman".split()},
          **{s: "east" for s in "wb odisha jharkhand assam arunachal manipur meghalaya mizoram nagaland sikkim tripura".split()}}
SHARE = {"maharashtra": "15%", "karnataka": "9%", "up": "8%", "tn": "7%", "delhi": "6%", "gujarat": "5%", "wb": "4%",
         "telangana": "4%", "rajasthan": "3%", "kerala": "3%"}           # from the handwritten notes
PRODUCT = {"fashion": "Apparel & fashion", "ethnic": "Ethnic fashion", "beauty": "Beauty", "grocery": "Online grocery",
           "premium": "Luxury & premium", "gifting": "Gifting", "mobacc": "Mobile accessories", "personal": "Personal care",
           "phones": "Smartphones", "appliances": "Large home appliances", "electronics": "Electronics", "winter": "Winter wear",
           "jewellery": "Jewellery", "footwear": "Footwear", "wedding": "Wedding registry items", "ac": "Air conditioners",
           "fridge": "Refrigerators", "homedecor": "Home decor & lights", "kitchen": "Kitchen & utensils",
           "sweets": "Sweets & festive food", "puja": "Puja items", "toys": "Toys & kites", "vehicles": "Vehicles",
           "travel": "Travel & stays", "stationery": "Books & stationery", "schoolgear": "School bags, uniforms & shoes",
           "laptops": "Laptops & tablets", "cooling": "Fans, coolers & cooling", "heating": "Heaters, geysers & blankets",
           "rainwear": "Umbrellas & rainwear", "airpurifier": "Air purifiers & masks", "health": "Health & wellness",
           "baby": "Baby & kids", "homeimprove": "Home improvement & repair", "sports": "Sports & fitness",
           "tv": "TVs & home entertainment", "furniture": "Furniture & mattresses", "agri": "Farm tools & agri inputs"}
CAT_FIX = {"apparel": "fashion", "smartphones": "phones", "sweets_food": "sweets", "kids": "baby"}

# Festival names -> one canonical id (ids that already exist in the page's notes layer are reused)
ALIAS = {
    "diwali": "diwali", "deepavali": "diwali", "deepawali": "diwali", "dipawali": "diwali", "divali": "diwali",
    "navratri": "navratri", "navaratri": "navratri", "navarathri": "navratri", "sharad navratri": "navratri",
    "dussehra": "dussehra", "dasara": "dussehra", "vijayadashami": "dussehra", "dussera": "dussehra",
    "durga puja": "durga", "kali puja": "kali", "shyama puja": "kali", "dhanteras": "dhanteras",
    "chhath": "chhath", "chhath puja": "chhath", "raksha bandhan": "rakhi", "rakhi": "rakhi", "rakshabandhan": "rakhi",
    "karwa chauth": "karwa", "karva chauth": "karwa", "lohri": "lohri",
    "eid al-fitr": "eid", "eid ul-fitr": "eid", "eid-ul-fitr": "eid", "id-ul-fitr": "eid", "ramzan eid": "eid",
    "ramadan eid": "eid", "eid": "eid", "ramzan": "eid", "eid al-adha": "bakrid", "eid ul-adha": "bakrid",
    "eid-ul-adha": "bakrid", "bakrid": "bakrid", "id-ul-zuha": "bakrid", "christmas": "christmas", "onam": "onam",
    "thiruvonam": "onam", "vishu": "vishu", "pongal": "pongal", "thai pongal": "pongal", "ugadi": "ugadi", "yugadi": "ugadi",
    "gudi padwa": "gudi", "holi": "holi", "ganesh chaturthi": "ganesh", "vinayaka chaturthi": "ganesh",
    "vinayaka chavithi": "ganesh", "vinayagar chaturthi": "ganesh", "ganeshotsav": "ganesh", "ganesh chavath": "ganesh",
    "ganesh utsav": "ganesh", "rongali bihu": "rangali", "bohag bihu": "rangali", "rangali bihu": "rangali",
    "bhogali bihu": "bhogali", "magh bihu": "bhogali", "kongali bihu": "f_kongali_bihu", "kati bihu": "f_kongali_bihu",
    "bestu varas": "gujny", "gujarati new year": "gujny", "makar sankranti": "sankranti", "sankranti": "sankranti",
    "makara sankranti": "sankranti", "makar sankranti / uttarayan": "sankranti", "bhai dooj": "bhaidooj",
    "bhai phonta": "bhaidooj", "bhau beej": "bhaidooj", "bhai tika": "bhaidooj", "independence day": "iday",
    "janmashtami": "f_janmashtami", "krishna janmashtami": "f_janmashtami", "gokulashtami": "f_janmashtami",
    "maha shivaratri": "f_mahashivratri", "mahashivratri": "f_mahashivratri", "maha shivratri": "f_mahashivratri",
    "shivratri": "f_mahashivratri", "akshaya tritiya": "f_akshaya_tritiya", "akha teej": "f_akshaya_tritiya",
    "baisakhi": "f_baisakhi", "vaisakhi": "f_baisakhi", "poila baishakh": "f_poila_baishakh",
    "pohela boishakh": "f_poila_baishakh", "bengali new year": "f_poila_baishakh", "rath yatra": "f_rath_yatra",
    "ratha yatra": "f_rath_yatra", "teej": "f_teej", "hariyali teej": "f_teej", "hartalika teej": "f_teej",
    "saraswati puja": "f_saraswati_puja", "vasant panchami": "f_saraswati_puja", "basant panchami": "f_saraswati_puja",
    "guru nanak jayanti": "f_guru_nanak_gurpurab", "guru nanak gurpurab": "f_guru_nanak_gurpurab",
    "gurpurab": "f_guru_nanak_gurpurab", "muharram": "f_muharram", "milad-un-nabi": "f_milad_un_nabi",
    "eid-e-milad": "f_milad_un_nabi", "good friday": "f_good_friday", "easter": "f_easter", "buddha purnima": "f_buddha_purnima",
    "ram navami": "f_ram_navami", "hanuman jayanti": "f_hanuman_jayanti", "mahavir jayanti": "f_mahavir_jayanti",
    "new year": "newyear", "valentine's day": "valentine",
}


def slug(s):
    return "f_" + re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def canon(name):
    low = name.lower().strip()
    parts = [low] + [p.strip() for p in re.split(r"[/(),&]| and |\+", low) if p.strip()]
    for p in parts:
        if p in ALIAS:
            return ALIAS[p]
    return slug(re.split(r"[/(]", name)[0].strip())


# same festival, different spellings across states -> one id
SLUG_FIX = {"f_sri_rama_navami": "f_ram_navami", "f_krishna_jayanthi": "f_janmashtami", "f_eid_e_milad_un_nabi": "f_milad_un_nabi",
            "f_vinayagar_chathurthi": "ganesh", "f_gowri_ganesha_habba": "ganesh", "f_ramadan_month": "f_ramadan",
            "f_saka_dawa": "f_saga_dawa", "f_kanwar_yatra_sawan": "f_kanwar_yatra", "f_karthika_masam_karthika_purnima": "f_karthika_purnima",
            "f_sabarimala_mandala_makaravilakku": "f_sabarimala_season", "f_vishwakarma_day": "f_vishwakarma_puja",
            "f_uttarayan": "sankranti", "f_pous_sankranti": "sankranti", "f_ayudha_pooja_and_vijayadasami": "dussehra",
            "f_navaratri_golu": "navratri", "f_independence_day_sales": "iday", "f_republic_day_sale_period": "f_republic_day",
            "f_kanwar": "f_kanwar_yatra"}
PER_STATE = {"f_state_day", "f_statehood_day", "f_formation_day"}   # generic names: keep one node per state


def months_of(f):
    ms = [int(m) for m in (f.get("months") or []) if 1 <= int(m) <= 12]
    return sorted(set(ms))


def main():
    groups = sorted(DEEP.glob("g*.json"))
    states, fest_names = [], {}
    for p in groups:
        data = json.loads(p.read_text())
        states.extend(data["states"])
    assert states, "no research files yet"
    db = FalkorDB(host="localhost", port=6380)
    g = db.select_graph(GRAPH)
    try:
        g.delete()
    except Exception:
        pass
    q = g.query
    q("UNWIND range(1,12) AS m CREATE (:Month {n:m, name:$names[m-1]})", {"names": MON})
    q("UNWIND $r AS r CREATE (:Region {id:r})", {"r": ["north", "west", "south", "east"]})
    q("UNWIND $p AS p CREATE (:Product {id:p.id, name:p.name})", {"p": [{"id": k, "name": v} for k, v in PRODUCT.items()]})
    for s in ["CREATE INDEX FOR (n:State) ON (n.id)", "CREATE INDEX FOR (n:Festival) ON (n.id)",
              "CREATE INDEX FOR (n:Product) ON (n.id)", "CREATE INDEX FOR (n:Signal) ON (n.id)", "CREATE INDEX FOR (n:Source) ON (n.url)"]:
        try:
            q(s)
        except Exception:
            pass
    n_rel = 0
    for s in states:
        sid = s["id"]
        q("""MATCH (r:Region {id:$r}) CREATE (st:State {id:$id, name:$name, share:$share, languages:$lang, culture:$cu,
             ecommerce:$ec}) CREATE (st)-[:IN_REGION]->(r)""",
          {"r": REGION[sid], "id": sid, "name": s["name"], "share": SHARE.get(sid, ""), "lang": s.get("languages", []),
           "cu": s.get("culture", ""), "ec": s.get("ecommerce", "")})
        for c in s.get("top_cities", [])[:5]:
            q("MATCH (st:State {id:$id}) MERGE (c:City {name:$c}) MERGE (st)-[:HAS_CITY]->(c)", {"id": sid, "c": c})
        for u in s.get("ecommerce_sources", [])[:3]:
            q("MATCH (st:State {id:$id}) MERGE (x:Source {url:$u}) MERGE (st)-[:CITES]->(x)", {"id": sid, "u": u})
        seen = set()
        rank = {"high": 0, "medium": 1, "low": 2}
        for f in sorted(s.get("festivals", []), key=lambda f: rank.get(f.get("impact"), 3)):
            fid = canon(f["name"])
            fid = SLUG_FIX.get(fid, fid)
            if fid in PER_STATE:
                fid = f"{fid}_{sid}"
            if fid in seen:          # two entries for the same festival in one state: keep the stronger one
                continue
            seen.add(fid)
            fest_names.setdefault(fid, f["name"].split("/")[0].split("(")[0].strip())
            cats = sorted({CAT_FIX.get(c, c) for c in f.get("categories", [])} & set(PRODUCT))
            q("""MERGE (fe:Festival {id:$fid}) ON CREATE SET fe.name=$name, fe.kind=$kind, fe.significance=$sig, fe.months=$ms
                 WITH fe MATCH (st:State {id:$sid})
                 CREATE (fe)-[:CELEBRATED_IN {impact:$imp, buys:$buys, reason:$why, date_2026:$d26, date_2027:$d27,
                         confidence:$conf, local_name:$ln, months:$ms, categories:$cats, sources:$src}]->(st)""",
              {"fid": fid, "name": fest_names[fid], "kind": f.get("kind", ""), "sig": f.get("significance", ""),
               "ms": months_of(f), "sid": sid, "imp": f.get("impact", "low"), "buys": f.get("buys", ""),
               "why": f.get("impact_reason", ""), "d26": f.get("date_2026"), "d27": f.get("date_2027"),
               "conf": f.get("confidence", ""), "ln": f.get("local_name", "") or "", "cats": cats,
               "src": f.get("sources", [])[:3]})
            n_rel += 1
            for c in cats:
                q("MATCH (fe:Festival {id:$fid}),(p:Product {id:$c}) MERGE (fe)-[d:DRIVES]->(p)", {"fid": fid, "c": c})
            for m in months_of(f):
                q("MATCH (fe:Festival {id:$fid}),(mo:Month {n:$m}) MERGE (fe)-[:IN_MONTH]->(mo)", {"fid": fid, "m": m})
            for u in f.get("sources", [])[:3]:
                q("MATCH (fe:Festival {id:$fid}) MERGE (x:Source {url:$u}) MERGE (fe)-[:CITES]->(x)", {"fid": fid, "u": u})
    # demand signals (school, weather, income, weddings, hold periods, sales, sports, tourism, health)
    sigs = []
    for f in ["sig_academic", "sig_weather", "sig_income", "sig_commerce"]:
        sigs += [x for x in json.loads((HERE / f"{f}.json").read_text())["signals"] if x["name"] != "Ramadan & Eid al-Fitr 2027"]
    for i, sg in enumerate(sigs):
        sgid = "s_" + re.sub(r"[^a-z0-9]+", "_", sg["name"].lower()).strip("_") + f"_{i}"
        cats = sorted({CAT_FIX.get(c, c) for c in sg["categories"]} & set(PRODUCT))
        q("""CREATE (s:Signal {id:$id, name:$name, type:$t, direction:$d, strength:$st, items:$it, reason:$r,
             national:$nat, months:$ms, src:$src})""",
          {"id": sgid, "name": sg["name"], "t": sg["type"], "d": sg["direction"], "st": sg["strength"], "it": sg.get("items", ""),
           "r": sg.get("reason", ""), "nat": sg["scope"] == "all", "ms": sg["months"], "src": sg.get("src", "")})
        if sg["scope"] != "all":
            q("MATCH (s:Signal {id:$id}) UNWIND $st AS x MATCH (st:State {id:x}) CREATE (s)-[:AFFECTS]->(st)",
              {"id": sgid, "st": sg["scope"]})
        rel = "CUTS" if sg["direction"] == "dip" else "LIFTS"
        q(f"MATCH (s:Signal {{id:$id}}) UNWIND $c AS x MATCH (p:Product {{id:x}}) CREATE (s)-[:{rel}]->(p)", {"id": sgid, "c": cats})
        q("MATCH (s:Signal {id:$id}) UNWIND $ms AS m MATCH (mo:Month {n:m}) CREATE (s)-[:IN_MONTH]->(mo)", {"id": sgid, "ms": sg["months"]})
        if sg.get("src"):
            q("MATCH (s:Signal {id:$id}) MERGE (x:Source {url:$u}) CREATE (s)-[:CITES]->(x)", {"id": sgid, "u": sg["src"]})
    stats = q("MATCH (n) RETURN labels(n)[0] AS l, count(*) AS c ORDER BY c DESC").result_set
    rels = q("MATCH ()-[r]->() RETURN count(r)").result_set[0][0]
    print("loaded:", {l: c for l, c in stats}, "relationships:", rels, "festival-state links:", n_rel)
    export(g)


def export(g):
    """Read everything back OUT of FalkorDB into the page's data format."""
    q = g.query
    out_states = []
    rows = q("""MATCH (st:State)-[:IN_REGION]->(r:Region)
                OPTIONAL MATCH (st)-[:CITES]->(x:Source)
                RETURN st.id, st.name, r.id, st.languages, st.culture, st.ecommerce, collect(x.url)""").result_set
    for sid, name, reg, lang, cu, ec, srcs in rows:
        fes = q("""MATCH (fe:Festival)-[c:CELEBRATED_IN]->(:State {id:$id})
                   RETURN fe.id, fe.name, c.months, fe.significance, c.buys, c.categories, c.impact, c.reason, c.sources,
                          c.date_2026, c.date_2027, c.confidence, fe.kind, c.local_name""", {"id": sid}).result_set
        out_states.append({"id": sid, "name": name, "r": reg, "l": lang, "cu": cu, "ec": ec, "es": (srcs or [""])[0],
                           "fe": [{"f": a, "n": b, "m": c or [], "s": d or "", "b": e or "", "c": f or [], "i": h or "low",
                                   "o": i or "", "u": (j or [""])[0], "d26": k, "d27": l, "cf": m, "k": n, "ln": o}
                                  for a, b, c, d, e, f, h, i, j, k, l, m, n, o in fes]})
    sigs = []
    for (sid, name, t, d, st, it, r, nat, ms, src) in q(
            "MATCH (s:Signal) RETURN s.id, s.name, s.type, s.direction, s.strength, s.items, s.reason, s.national, s.months, s.src").result_set:
        states = [x[0] for x in q("MATCH (:Signal {id:$id})-[:AFFECTS]->(st:State) RETURN st.id", {"id": sid}).result_set]
        cats = [x[0] for x in q("MATCH (:Signal {id:$id})-[:LIFTS|CUTS]->(p:Product) RETURN p.id", {"id": sid}).result_set]
        sigs.append({"name": name, "type": t, "direction": d, "strength": st, "items": it, "reason": r,
                     "scope": "all" if nat else states, "months": ms, "categories": cats, "src": src})
    evidence = json.loads((HERE / "evidence.json").read_text())
    blob = {"states": out_states, "evidence": evidence, "signals": sigs,
            "meta": {"source": "FalkorDB graph india_ecom", "states": len(out_states),
                     "festivals": q("MATCH (f:Festival) RETURN count(f)").result_set[0][0],
                     "links": q("MATCH ()-[r]->() RETURN count(r)").result_set[0][0]}}
    (HERE / "webdata.json").write_text(json.dumps(blob, ensure_ascii=False, separators=(",", ":")))
    print("exported webdata.json:", blob["meta"])


if __name__ == "__main__":
    main()
