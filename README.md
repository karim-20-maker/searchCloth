# searchCloth — صيّاد الأسعار

بتكتب اسم المنتج (مثلاً `Ralph Lauren jacket`) وتختار الدولة، والتطبيق بيرجعلك كل الأسعار مترتبة من الأرخص، مع نوع المتجر (أوتليت / متجر الماركة / متجر عادي).

## التشغيل
1. اعمل حساب مجاني على https://serpapi.com وخد الـ API key.
2. شغّل:
   ```
   SERPAPI_KEY=مفتاحك python3 server.py
   ```
3. افتح http://localhost:8000

من غير مفتاح بيشتغل بداتا تجريبية (Demo). محتاج Python 3.8+ بس، من غير مكتبات.

## النشر المجاني (زي كوتشي)
- **الواجهة:** GitHub Pages (Settings → Pages → Branch: main / root).
- **المفتاح:** Cloudflare Worker مجاني. اعمل Worker جديد، الصق فيه `worker.js`، وضيف Secret باسم `SERPAPI_KEY`.
- بعدين حط لينك الـ Worker في `API_BASE` جوه `index.html`.
