// Cloudflare Worker (مجاني) - بيخبّي مفتاح SerpApi ويرد على الواجهة اللي على GitHub Pages
// الإعداد: Settings > Variables and Secrets > SERPAPI_KEY (Secret)
const ALLOWED_ORIGIN = "https://karim-20-maker.github.io";
const COUNTRIES = ["ca","us","gb","ae","sa","eg","de","fr","it","es","tr","au","nl","qa","kw"];
const OUTLET = ["outlet","rack","tjmaxx","t.j.maxx","marshalls","winners","ssense","yoox","outnet","zalando","sale","clearance","discount","off 5th","saks off","farfetch","thebay","hudson's bay","ebay"];

const cors = { "Access-Control-Allow-Origin": ALLOWED_ORIGIN, "Content-Type": "application/json" };
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: cors });

function classify(source, q) {
  const s = source.toLowerCase();
  if (OUTLET.some(h => s.includes(h))) return "outlet";
  const words = (q.toLowerCase().match(/[a-z]+/g) || []).filter(w => w.length > 3);
  return words.some(w => s.includes(w)) ? "brand" : "store";
}
function relevant(title, q) {
  const toks = (q.toLowerCase().match(/\w+/g) || []).filter(t => t.length > 2);
  if (!toks.length) return true;
  const hit = toks.filter(t => title.toLowerCase().includes(t)).length;
  return hit >= Math.max(1, Math.floor(toks.length / 2));
}

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS")
      return new Response(null, { headers: { ...cors, "Access-Control-Allow-Methods": "GET" } });
    const u = new URL(req.url);
    const q = (u.searchParams.get("q") || "").trim().slice(0, 120);
    const c = u.searchParams.get("country") || "us";
    if (!q || !COUNTRIES.includes(c)) return json({ error: "اكتب اسم المنتج واختار دولة" }, 400);
    if (!env.SERPAPI_KEY) return json({ error: "المفتاح مش متضاف في الـ Worker" }, 500);
    const api = new URL("https://serpapi.com/search.json");
    api.search = new URLSearchParams({ engine: "google_shopping", q, gl: c, hl: "en", num: "40", api_key: env.SERPAPI_KEY });
    const r = await fetch(api);
    if (!r.ok) return json({ error: "فشل البحث (" + r.status + ")" }, 502);
    const data = await r.json();
    const results = (data.shopping_results || [])
      .filter(i => i.extracted_price != null && relevant(i.title || "", q))
      .map(i => ({
        title: i.title || "", store: i.source || "", kind: classify(i.source || "", q),
        price: i.extracted_price, price_text: i.price || String(i.extracted_price),
        old_price: i.extracted_old_price || null, link: i.product_link || i.link || "",
        image: i.thumbnail || "", delivery: i.delivery || "", rating: i.rating || null }))
      .sort((a, b) => a.price - b.price);
    return json({ results, demo: false });
  }
};
