# India E-commerce Knowledge Graph

Interactive 3D demand map of Indian e-commerce: 36 states and UTs, 343 festivals (15-25 researched per state, with 2026 and 2027 dates and a verification pass) 314 specific products (kites, rakhis, mekhela sador, bonam pots...) and 134 demand signals (school calendars, weather, harvest income, weddings, hold periods, sales, sports, tourism), turned into month-by-state push/hold plans.

Live: https://thinkvas.github.io/india-ecommerce-graph/

Views: **Graph on map** (the FalkorDB knowledge graph in 3D over India: states on the map, festivals floating above the states that celebrate them, specific products above the festivals; click anything to light up its chain), network, year wheel and 3D graph. `data/kgraph.json` is the raw node/relationship export from FalkorDB that this view draws.

**Draw an area** (Graph on map view): draw a polygon or circle anywhere on India and get what is happening inside it: states covered and estimated share of online orders (people-weighted), festivals now and next month, demand signals, the products to push and hold (from the FalkorDB graph), live 7-day weather from [Open-Meteo](https://open-meteo.com) with the products it triggers, and shops, markets and towns from [OpenStreetMap](https://www.openstreetmap.org) (Overpass API). "Copy this area as JSON" gives the same result for apps. Aggregates only, no personal data.

QA: `tools/qa_harness.js` runs every state x month plan, every map focus and every view; expert-review issues and fix logs are in `qa/` (not published).

Map boundaries: [Datameet](https://github.com/datameet/maps) state boundaries (States/Admin2), simplified by `data/geo_build.py`.

## Data: FalkorDB is the master

All research lives in a FalkorDB graph (`india_ecom`). The page is an export of that graph.

```
(:Festival)-[:CELEBRATED_IN {impact, buys, date_2026, date_2027, confidence, sources}]->(:State)-[:IN_REGION]->(:Region)
(:Festival)-[:DRIVES]->(:Product)      (:Festival)-[:IN_MONTH]->(:Month)
(:Festival)-[:NEEDS {states}]->(:Item)-[:IS_A]->(:Product)      (:Signal)-[:LIFTS_ITEM|CUTS_ITEM]->(:Item)
(:Signal)-[:AFFECTS]->(:State)         (:Signal)-[:LIFTS|CUTS]->(:Product)
(:State)-[:HAS_CITY]->(:City)          (:State|Festival)-[:CITES]->(:Source)
```

Rebuild the graph from the research files:

```
docker run -d -p 6380:6379 -p 3010:3000 falkordb/falkordb
pip install falkordb
python data/falkor_load.py      # loads data/deep/g*.json + data/sig_*.json, exports data/webdata.json
```

Browse it at http://localhost:3010 (FalkorDB Browser), e.g.
`MATCH (f:Festival)-[r:CELEBRATED_IN {impact:'high'}]->(s:State {id:'telangana'}) RETURN f.name, r.date_2026, r.buys`

`data/deep/g*.verify.md` lists every correction made in the verification pass and what is still uncertain.
