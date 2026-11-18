#!/usr/bin/env python3
"""PriceHunter - بيدور على أرخص سعر لأي هدوم في أي دولة.
بدون مكتبات خارجية. التشغيل:  SERPAPI_KEY=xxxx python3 server.py
من غير مفتاح بيشتغل بداتا تجريبية (Demo)."""
import json, os, re, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEY = os.environ.get("SERPAPI_KEY", "")
PORT = int(os.environ.get("PORT", "8000"))
HERE = os.path.dirname(os.path.abspath(__file__))

COUNTRIES = {  # كود جوجل -> الاسم
    "ca": "كندا", "us": "أمريكا", "gb": "بريطانيا", "ae": "الإمارات", "sa": "السعودية",
    "eg": "مصر", "de": "ألمانيا", "fr": "فرنسا", "it": "إيطاليا", "es": "إسبانيا",
    "tr": "تركيا", "au": "أستراليا", "nl": "هولندا", "qa": "قطر", "kw": "الكويت",
}
OUTLET_HINTS = ["outlet", "rack", "tjmaxx", "t.j.maxx", "marshalls", "winners", "ssense",
                "yoox", "outnet", "zalando", "sale", "clearance", "discount", "off 5th",
                "saks off", "farfetch", "thebay", "hudson's bay", "nordstrom rack", "ebay"]

def classify(source, query):
    s = source.lower()
    if any(h in s for h in OUTLET_HINTS):
        return "outlet"
    words = [w for w in re.findall(r"[a-z]+", query.lower()) if len(w) > 3]
    if any(w in s for w in words):
        return "brand"   # غالبًا المتجر الرسمي للماركة
    return "store"

def relevant(title, query):
    toks = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
    if not toks:
        return True
    hit = sum(t in title.lower() for t in toks)
    return hit >= max(1, len(toks) // 2)

def search(q, country):
    if not KEY:
        return demo(q, country), True
    params = urllib.parse.urlencode({
        "engine": "google_shopping", "q": q, "gl": country, "hl": "en",
        "num": 40, "api_key": KEY})
    with urllib.request.urlopen("https://serpapi.com/search.json?" + params, timeout=25) as r:
        data = json.load(r)
    out = []
    for it in data.get("shopping_results", []):
        price = it.get("extracted_price")
        if price is None or not relevant(it.get("title", ""), q):
            continue
        src = it.get("source", "")
        out.append({
            "title": it.get("title", ""), "store": src, "kind": classify(src, q),
            "price": price, "price_text": it.get("price", str(price)),
            "old_price": it.get("extracted_old_price"),
            "link": it.get("product_link") or it.get("link", ""),
            "image": it.get("thumbnail", ""), "delivery": it.get("delivery", ""),
            "rating": it.get("rating")})
    out.sort(key=lambda x: x["price"])
    return out, False

def demo(q, country):
    rows = [("Nordstrom Rack", 129.99, 398), ("Ralph Lauren", 249.0, None), ("SSENSE", 189.0, 295),
            ("Winners", 99.99, None), ("Hudson's Bay", 219.0, 325), ("eBay", 85.0, None)]
    return sorted([{
        "title": f"{q} (بيانات تجريبية)", "store": s, "kind": classify(s, "ralph lauren"),
        "price": p, "price_text": f"${p:,.2f}", "old_price": o, "link": "https://example.com",
        "image": "", "delivery": "", "rating": None} for s, p, o in rows], key=lambda x: x["price"])

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            return self._send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        if u.path == "/api/countries":
            return self._send(200, json.dumps(COUNTRIES), "application/json")
        if u.path == "/api/search":
            qs = urllib.parse.parse_qs(u.query)
            q = qs.get("q", [""])[0].strip(); c = qs.get("country", ["us"])[0]
            if not q or c not in COUNTRIES:
                return self._send(400, json.dumps({"error": "اكتب اسم المنتج واختار دولة"}), "application/json")
            try:
                res, is_demo = search(q, c)
            except Exception as e:
                return self._send(502, json.dumps({"error": f"فشل البحث: {e}"}), "application/json")
            return self._send(200, json.dumps({"results": res, "demo": is_demo}), "application/json")
        self._send(404, "not found", "text/plain")

if __name__ == "__main__":
    print(f"شغال على http://localhost:{PORT}  ({'LIVE' if KEY else 'DEMO - من غير SERPAPI_KEY'})")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
