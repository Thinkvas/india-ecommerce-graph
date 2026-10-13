# Research brief: festivals that move e-commerce, per Indian state/UT

You are a senior India retail & e-commerce analyst. For EACH state/UT assigned to you, find 15-25 festivals/fairs/observances
that matter for consumer spending (major pan-Indian ones as observed there AND local/regional/tribal ones, regional new years,
harvest festivals, community-specific festivals, big fairs/melas). Use WebSearch + WebFetch. Prefer: state tourism/government
sites, drikpanchang / official holiday lists for DATES, reputable news (The Hindu, Times of India, Indian Express, Hindustan Times,
regional papers), business media (Economic Times, Mint, Business Standard, afaqs, exchange4media), platform press releases
(Amazon, Flipkart, Meesho, Myntra, Nykaa), CAIT trade estimates. OPEN pages to verify; do not invent.

For each festival give:
- name (common English spelling), local_name (in Latin script, optional)
- kind: one of religious | harvest | new_year | cultural | tribal | fair | national
- months: typical month numbers (1-12)
- date_2026 and date_2027: "YYYY-MM-DD" or "YYYY-MM-DD..YYYY-MM-DD" (main day or range); null if unknown
- significance: 1 line
- buys: specific items people buy (e.g. "pattu sarees, gold, kites, new clothes")
- categories: ONLY from this list: fashion,ethnic,beauty,grocery,premium,gifting,mobacc,personal,phones,appliances,electronics,
  winter,jewellery,footwear,wedding,ac,fridge,homedecor,kitchen,sweets,puja,toys,vehicles,travel,stationery,schoolgear,laptops,
  cooling,heating,rainwear,airpurifier,health,baby,homeimprove,sports,tv,furniture,agri
- impact: high | medium | low  (e-commerce/online-shopping impact, not just cultural size)
- impact_reason: 1 line (why online demand rises or not; mention evidence numbers if found)
- sources: 1-3 URLs you opened
- confidence: high | medium | low

Also per state: languages, top_cities (3-5), culture (shopping traits, 1-2 lines), ecommerce (facts with numbers if any),
ecommerce_sources (URLs).

WRITE the result as valid JSON (UTF-8) to the file path you are given, shape:
{"group":"g1","states":[{"id":"up","name":"Uttar Pradesh","languages":[...],"top_cities":[...],"culture":"...","ecommerce":"...",
 "ecommerce_sources":[...],"festivals":[{...}]}]}
Use ONLY these state ids: up,bihar,delhi,punjab,haryana,chandigarh,hp,jk,ladakh,uttarakhand,rajasthan,maharashtra,gujarat,goa,mp,cg,
dnhdd,ap,telangana,karnataka,tn,kerala,puducherry,lakshadweep,andaman,wb,odisha,jharkhand,assam,arunachal,manipur,meghalaya,
mizoram,nagaland,sikkim,tripura.
Keep strings short (<200 chars). After writing, validate the file parses as JSON (python3 -c "import json;json.load(open(PATH))").
Your final reply: just a 3-line summary (states done, festival counts, anything you could not verify).
