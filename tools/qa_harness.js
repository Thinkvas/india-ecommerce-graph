// QA harness: paste into the page console (served by tools/qa_server.py). Runs every state x month plan,
// every map focus, every view; POSTs qa/plans.json + qa/autotest.json back to the server.
(async () => {
const errs = [], plans = [], issues = [];
const lab = i => byId.get(iid(i))?.label || i;
const states = N.filter(d => d.type === "state");
for (const s of states) for (let m = 1; m <= 12; m++) { try {
  const p = monthPlan(s.id, m);
  plans.push({ state: s.label, id: s.id, month: MON[m - 1], year: yearFor(m),
    fests: p.fs.map(x => x.f.label + (x.lead ? " (pre-push)" : "") + " [" + (x.date || "no date") + "] " + (["", "low", "medium", "high"][Math.round(x.lead ? x.w * 2 : x.w)] || "")),
    signals: p.sigs.map(g => (g.dir < 0 ? "HOLD " : "") + g.label + (g.national ? " (all-India)" : "")),
    items: p.items.map(x => ({ p: lab(x.i), cat: ITEMS[x.i].c, why: x.why.map(r => r.label + (r.d ? " [" + r.d + "]" : "")).join(" + "), watch: (x.watch || []).map(r => r.label).join(", ") })),
    holdItems: p.holdItems.map(x => lab(x.i) + " <- " + x.why.map(r => r.label).join("+")),
    rank: board(m).findIndex(x => x.s.id === s.id) + 1 });
  if (p.items.length < 4) issues.push(`${s.id}-${m}: only ${p.items.length} products`);
  const both = p.items.filter(x => p.holdItems.some(h => h.i === x.i)); if (both.length) issues.push(`${s.id}-${m}: push+hold ${both.map(x => lab(x.i))}`);
  p.fs.forEach(x => { if (!x.lead && x.date && !monthsOfDate(x.date).includes(m)) issues.push(`${s.id}-${m}: ${x.f.label} date ${x.date} not in month`); });
} catch (e) { errs.push(`${s.id}-${m}: ${e.message}`); } }
setView("map"); await new Promise(r => setTimeout(r, 800));
const mapErr = [], sizes = [];
const ids = [...states.map(s => s.id), ...N.filter(d => ["festival", "item", "signal"].includes(d.type)).map(d => d.id)];
for (const id of ids) for (const mm of [null, 5, 10]) { try {
  selected = id; month = mm; const md = mapModel();
  const bad = [...md.hot].filter(h => { const n = KN.get(h); return !n || !pos3(n).every(Number.isFinite); });
  if (bad.length) mapErr.push(id + " bad pos " + bad.slice(0, 3)); sizes.push([id, mm, md.hot.size]);
} catch (e) { mapErr.push(id + "/" + mm + ": " + e.message); } }
selected = null; month = null;
const viewErr = []; for (const v of ["net", "wheel", "3d", "map"]) { try { setView(v); await new Promise(r => setTimeout(r, 500)); } catch (e) { viewErr.push(v + ": " + e.message); } }
const big = sizes.filter(x => x[2] > 30).map(x => x.join(":"));
await fetch("/dump/plans.json", { method: "POST", body: JSON.stringify(plans) });
await fetch("/dump/autotest.json", { method: "POST", body: JSON.stringify({ errs, issues, mapErr, big, viewErr }, null, 1) });
window.__qa = [plans.length, errs.length, issues.length, mapErr.length, big.length, viewErr.length];
})();
