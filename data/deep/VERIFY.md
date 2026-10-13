# Verify pass brief (Indian state festivals -> e-commerce)

You are checking research files deep/gN.json (format described in deep/BRIEF.md - read it first).
Goal: make the data ACCURATE. Edit the JSON files IN PLACE (keep the exact same schema), then write a short log deep/gN.verify.md per file.

For each assigned file:
1. Every festival with impact "high" or "medium": verify date_2026 (and date_2027 if given) against a reliable source
   (drikpanchang.com, the state's official gazetted holiday list, timeanddate.com, official tourism sites). Fix wrong dates;
   if you cannot confirm, set confidence "low" (do not invent). Dates are "YYYY-MM-DD" or ranges as already used in the file.
2. "months" must match date_2026 (1-12 ints). Fix mismatches.
3. Impact sanity: "high" only if the festival clearly drives big online/retail buying in that state (gifting, apparel, gold,
   electronics, puja kits, etc.). Downgrade obvious over-ratings (e.g. a small local temple fair marked high). Upgrade only with evidence.
4. Remove exact duplicates within a state (same festival twice under two names). Keep the richer entry.
5. "categories" must stay within the fixed allowed list in BRIEF.md. All strings < 200 chars.
6. Do not delete festivals just because they are low impact. Do not add new fields.
After editing, run: python3 -c "import json;json.load(open('deep/gN.json'))" to confirm valid JSON.
The log should list: what you changed (festival, field, old -> new, source URL) and what remains uncertain. Keep it under 40 lines.
Final report to me: 3-6 lines, counts of fixes per state.
