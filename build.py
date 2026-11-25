#!/usr/bin/env python3
"""PayoutMath static site generator.

Reads data/fees.json and writes a complete static site to dist/.
No dependencies beyond Python 3 and Node (Node is only used to run the same
fee engine the browser uses, so every number printed on a page matches the
live calculator).

Config through environment variables:
  SITE_URL      full public URL, no trailing slash   (default https://payoutmath.pages.dev)
  BASE_PATH     path prefix if served from a sub-folder, e.g. /payoutmath (default empty)
  CROSSLIST_URL affiliate link for Crosslist once the account exists (default plain site)
  GSC_TOKEN     Google Search Console verification token (optional)
"""
import html, json, os, shutil, subprocess, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
FEES = json.loads((ROOT / "data/fees.json").read_text())
SITE_URL = (os.environ.get("SITE_URL") or "https://payoutmath.pages.dev").rstrip("/")
BASE = (os.environ.get("BASE_PATH") or "").rstrip("/")
CROSSLIST_URL = os.environ.get("CROSSLIST_URL") or "https://crosslist.com/"
GSC = os.environ.get("GSC_TOKEN", "")
BRAND = "PayoutMath"
YEAR = FEES["checked"][:4]
CHECKED = datetime.date.fromisoformat(FEES["checked"]).strftime("%B %-d, %Y")
MARKETS = ["ebay", "poshmark", "mercari", "depop", "etsy", "whatnot"]
PRICES = [10, 15, 20, 25, 30, 40, 50, 75, 100, 200]
TAX = 7  # default buyer sales tax % used in examples
esc = html.escape

# ---------------------------------------------------------------- fee engine
def engine(jobs):
    """Run many calc jobs through src/calc.js in one Node process."""
    script = (
        "const PM=require(process.argv[1]),F=require(process.argv[2]);"
        "const jobs=JSON.parse(require('fs').readFileSync(0,'utf8'));"
        "process.stdout.write(JSON.stringify(jobs.map(j=>j.compare?PM.compare(F,j.x):"
        "j.target!==undefined?PM.priceFor(F,j.k,j.x,j.target):PM.calc(F,j.k,j.x))));"
    )
    out = subprocess.run(["node", "-e", script, str(ROOT / "src/calc.js"), str(ROOT / "data/fees.json")],
                         input=json.dumps(jobs), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)

def calc(k, **x): return engine([{"k": k, "x": x}])[0]
def money(n): return ("-$" if n < 0 else "$") + f"{abs(n):,.2f}"
def url(p): return f"{BASE}/{p}" if p else f"{BASE}/"
def abs_url(p): return f"{SITE_URL}{url(p)}"

# ---------------------------------------------------------------- copy
TIPS = {
    "ebay": [
        "eBay charges its percentage on the whole order: item price, the shipping the buyer pays, and sales tax. Overcharging for shipping costs you fees too.",
        "The per-order fee is $0.30 on orders of $10 or less and $0.40 above that, so very cheap items lose a big share to fixed fees. Bundle them.",
        "Promoted Listings are optional and charged only when the item sells. Add your ad rate in the calculator to see what it really costs.",
        "You get 250 free listings a month; after that each listing costs $0.35."],
    "poshmark": [
        "Under $15 Poshmark takes a flat $2.95, which is close to 30% on a $10 item. Bundling cheap items into one sale over $15 keeps more for you.",
        "At $15 and up the fee is 20% of the sale price. There's no extra payment processing fee and no listing fee.",
        "Buyers pay for the prepaid shipping label, so shipping doesn't change your payout."],
    "mercari": [
        "Mercari takes a flat 10% of the item price plus any shipping the buyer pays. There's no separate payment processing fee.",
        "Withdrawing by direct deposit is free once a day; Instant Pay costs $3, which adds up on small sales.",
        "Buyers pay a separate 3.6% buyer protection fee. It doesn't come out of your payout."],
    "depop": [
        "US sellers pay no selling fee on Depop, only payment processing of 3.3% + $0.45 on the full transaction including shipping and tax.",
        "The fixed $0.45 matters most on cheap items: on a $10 sale it's almost 5% by itself.",
        "Boosted listings add a boost fee only if the item sells through the boost. Turn boost on in the calculator to see the difference.",
        "Buyers pay a marketplace fee at checkout; it doesn't come out of your payout."],
    "etsy": [
        "Etsy's core fees are a $0.20 listing fee, 6.5% on item plus shipping, and 3% + $0.25 payment processing on the order total including tax.",
        "The $0.20 listing fee is charged even if the item never sells, and again on each four-month renewal.",
        "Offsite Ads add 15% (12% once your shop passes $10,000 a year) when a sale comes from an Etsy ad, capped at $100 per order."],
    "whatnot": [
        "Whatnot's 8% commission is charged on the sale price only, not shipping or tax. Processing is 2.9% + $0.30 on the full order.",
        "In comics, trading cards, sports singles, and toys and hobbies, commission drops to 0% on the part of a sale above $1,500 (a limited-time rule).",
        "Coins and money pay a 4% commission up to $1,500."],
    "paypal": [
        "Goods and services payments sent to you cost 2.99% with no fixed fee.",
        "PayPal Checkout on a website, and Pay with Venmo, cost 3.49% + $0.49 per transaction.",
        "Payments from outside the US add 1.5%."],
}

OPTIONS = {
    "ebay": lambda F: '<div class=full><label for=ebayCat>Category</label><select id=ebayCat>' +
        "".join(f'<option value="{k}">{esc(v["label"])}</option>' for k, v in F["categories"].items()) +
        '</select></div><div><label for=adRate>Promoted listing ad rate (%)</label><input id=adRate type=number min=0 step=0.1 value=0 inputmode=decimal></div>',
    "depop": lambda F: '<div><label class=check><input id=boost type=checkbox> Sold through a boost</label></div>'
        f'<div><label for=boostRate>Boost rate (%)</label><input id=boostRate type=number min=0 step=0.1 value={F["boost_default"]*100:g} inputmode=decimal></div>',
    "etsy": lambda F: '<div><label class=check><input id=offsite type=checkbox> Sale came from Offsite Ads</label></div>'
        '<div><label class=check><input id=bigShop type=checkbox> Shop sells over $10k a year</label></div>',
    "whatnot": lambda F: '<div class=full><label for=wnCat>Category</label><select id=wnCat>' +
        "".join(f'<option value="{k}">{esc(v["label"])}</option>' for k, v in F["categories"].items()) + '</select></div>',
    "paypal": lambda F: '<div class=full><label for=ppMode>Payment type</label><select id=ppMode>' +
        "".join(f'<option value="{k}">{esc(v["label"])}</option>' for k, v in F["modes"].items()) +
        '</select></div><div class=full><label class=check><input id=intl type=checkbox> Payment from outside the US</label></div>',
}

# ---------------------------------------------------------------- layout
def page(path, title, desc, body, schema=None, crumbs=None):
    canon = abs_url(path)
    ld = ""
    blocks = list(schema or [])
    if crumbs:
        blocks.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p)} for i, (n, p) in enumerate(crumbs)]})
    for b in blocks:
        ld += '<script type="application/ld+json">' + json.dumps(b, separators=(",", ":")).replace("</", "<\\/") + "</script>\n"
    crumb_html = ""
    if crumbs:
        crumb_html = '<div class="crumbs wrap">' + " / ".join(
            f'<a href="{url(p)}">{esc(n)}</a>' for n, p in crumbs[:-1]) + f" / {esc(crumbs[-1][0])}</div>"
    gsc = f'<meta name="google-site-verification" content="{esc(GSC)}">' if GSC else ""
    doc = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}"><meta property="og:site_name" content="{BRAND}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{url('favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{url('style.css')}">
{gsc}
{ld}</head><body>
<header class="site"><div class="wrap"><a class="logo" href="{url('')}">Payout<span>Math</span></a>
<nav class="top"><a href="{url('')}">Compare</a><a href="{url('marketplace-fees/')}">All fees</a><a href="{url('reseller-profit-tracker/')}">Free tracker</a></nav></div></header>
{crumb_html}
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
<p><b>{BRAND}</b> is a free set of seller fee calculators for resellers. Fees last checked {CHECKED} against each platform's published fee pages. Estimates only; your platform's sales report is the final word.</p>
<p><a href="{url('about/')}">About</a> · <a href="{url('privacy/')}">Privacy</a> · <a href="{url('marketplace-fees/')}">Fee sources</a></p>
<p class="note">Some links are affiliate links: if you sign up through them we may earn a commission at no cost to you.</p>
</div></footer>
</body></html>"""
    out = DIST / path / "index.html" if path else DIST / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    SITEMAP.append(canon)

SITEMAP = []

def calc_block(mode, key=None, title="Your sale"):
    opts = OPTIONS[key](FEES["platforms"][key]) if key in OPTIONS else ""
    is_posh = key == "poshmark"
    ship_fields = "" if is_posh else """
<div><label for=ship>Shipping the buyer pays ($)</label><input id=ship type=number min=0 step=0.01 value=0 inputmode=decimal></div>
<div><label for=shipCost>Your shipping cost ($)</label><input id=shipCost type=number min=0 step=0.01 value=0 inputmode=decimal></div>"""
    tax = "" if key in ("poshmark", "mercari", "paypal") else f"""
<div><label for=taxRate>Buyer's sales tax (%)</label><input id=taxRate type=number min=0 step=0.1 value={TAX} inputmode=decimal></div>"""
    reverse = "" if mode == "compare" else """
<div class=full><label for=target>Target profit ($), to find the price you need</label><input id=target type=number step=0.01 value=10 inputmode=decimal></div>"""
    cost_label = "Amount received ($)" if key == "paypal" else "Sale price ($)"
    cost = "" if key == "paypal" else """
<div><label for=cost>What you paid for the item ($)</label><input id=cost type=number min=0 step=0.01 value=0 inputmode=decimal></div>"""
    return f"""<section id="pm" class="calc" data-mode="{mode}" data-platform="{key or ''}" data-base="{BASE}">
<div class="card"><h2 style="margin-top:0">{esc(title)}</h2><div class="fields">
<div><label for=price>{cost_label}</label><input id=price type=number min=0 step=0.01 value=30 inputmode=decimal></div>
{cost}{ship_fields}{tax}{opts}{reverse}
</div></div>
<div class="card" aria-live="polite"><div id="result"></div><p id="reverse" class="note" style="margin-top:12px"></p></div>
</section>
<script src="{url('fees.js')}"></script><script src="{url('calc.js')}"></script><script src="{url('ui.js')}"></script>"""

def cta():
    return f"""<div class="cta"><b>Selling on more than one of these?</b>
<p>Listing the same item on eBay, Poshmark, Mercari and Depop by hand takes hours. A crosslisting tool copies one listing to all of them and delists everywhere when it sells.</p>
<a class="btn" href="{esc(CROSSLIST_URL)}" rel="sponsored noopener" target="_blank">Try Crosslist</a></div>"""

def faq_html(qa):
    return "<h2>Questions sellers ask</h2>" + "".join(
        f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qa)

def faq_schema(qa):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}

def app_schema(name, path, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": abs_url(path),
            "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "description": desc,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}

# ---------------------------------------------------------------- build
def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for f in ("calc.js", "ui.js", "style.css"):
        shutil.copy(ROOT / "src" / f, DIST / f)
    (DIST / "fees.js").write_text("window.FEES=" + json.dumps(FEES, separators=(",", ":")) + ";")
    (DIST / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#0f7b5f"/><text x="16" y="22" font-size="18" text-anchor="middle" fill="#fff" font-family="sans-serif" font-weight="700">$</text></svg>')
    P = FEES["platforms"]

    # Precompute every number the static pages print.
    jobs = []
    for k in MARKETS:
        for p in PRICES:
            jobs.append({"k": k, "x": {"price": p}})
            jobs.append({"k": k, "x": {"price": p, "taxRate": TAX}})
    res = iter(engine(jobs))
    table = {k: {p: (next(res), next(res)) for p in PRICES} for k in MARKETS}

    # ---- platform calculator pages
    for k, F in P.items():
        path = F["slug"] + "/"
        title = f"{F['keyword']} ({YEAR}): fees, payout and profit"
        desc = f"Free {F['keyword'].lower()} updated for {YEAR}. See exactly what {F['name']} takes, what you get paid and your real profit after shipping and item cost."
        ex = ""
        if k in MARKETS:
            rows = "".join(
                f"<tr><td><a href='{url(f'how-much-does-{k}-take-from-{p}/')}'>{money(p)}</a></td><td class=n>{money(table[k][p][0]['fees'])}</td>"
                f"<td class=n>{money(table[k][p][0]['payout'])}</td><td class=n>{table[k][p][0]['feePct']}%</td></tr>" for p in PRICES)
            ex = f"""<h2>What {F['name']} takes at common prices</h2>
<p class=note>Item price only, no shipping, standard category, no sales tax. Click a price for the full breakdown.</p>
<div class=table-scroll><table><thead><tr><th>Sale</th><th class=n>{F['name']} takes</th><th class=n>You get</th><th class=n>Fee rate</th></tr></thead><tbody>{rows}</tbody></table></div>"""
        r50 = calc(k, price=50, ship=0) if k != "paypal" else calc(k, price=100)
        qa = [
            (f"How much does {F['name']} take from a sale in {YEAR}?", F["summary"]),
            (f"How much does {F['name']} take from a $50 sale?" if k != "paypal" else "What is the PayPal fee on $100?",
             (f"About {money(r50['fees'])} with no shipping or sales tax, so you're paid {money(r50['payout'])}." if k != "paypal"
              else f"For a goods and services payment, {money(r50['fees'])}, so you receive {money(r50['payout'])}.")),
            ("Are these numbers exact?", f"They follow {F['name']}'s published US fee rules as of {CHECKED}. Taxes, promotions and account-specific rates can change the final amount, so check your sales report for the exact figure."),
        ]
        others = " · ".join(f"<a href='{url(P[o]['slug'] + '/')}'>{P[o]['name']}</a>" for o in P if o != k)
        body = f"""<h1>{esc(F['keyword'])}</h1>
<p class=lede>Enter your sale and see what {esc(F['name'])} takes, what lands in your account and what you actually profit. Updated {CHECKED}.</p>
{calc_block('single', k, f'Your {F["name"]} sale')}
<h2>How {esc(F['name'])} fees work</h2>
<ul>{''.join(f'<li>{esc(t)}</li>' for t in TIPS[k])}</ul>
{ex}
{cta() if k != 'paypal' else ''}
<p><a href="{url('')}">Compare this sale across every marketplace →</a></p>
{faq_html(qa)}
<p class=note>Source: <a href="{esc(F['source'])}" rel="nofollow noopener" target="_blank">{esc(F['source_note'])}</a>, checked {CHECKED}.</p>
<p class=note>Other calculators: {others}</p>"""
        page(path, title, desc, body, [app_schema(F["keyword"], path, desc), faq_schema(qa)],
             [("Home", ""), (F["keyword"], path)])

    # ---- "how much does X take from $N" pages
    cmp_jobs = [{"compare": True, "x": {"price": p}} for p in PRICES]
    cmp = dict(zip(PRICES, engine(cmp_jobs)))
    for k in MARKETS:
        F = P[k]
        for p in PRICES:
            r, rt = table[k][p]
            path = f"how-much-does-{k}-take-from-{p}/"
            title = f"How much does {F['name']} take from ${p}? ({YEAR})"
            desc = f"{F['name']} takes {money(r['fees'])} from a ${p} sale, so you get {money(r['payout'])}. Full fee breakdown and how other marketplaces compare."
            lines = "".join(f"<tr><td>{esc(a)}</td><td class=n>{money(b)}</td></tr>" for a, b in r["lines"])
            others = "".join(
                f"<tr{' class=rank1' if i == 0 else ''}><td><a href='{url(f'how-much-does-{o['key']}-take-from-{p}/')}'>{o['name']}</a></td><td class=n>{money(o['fees'])}</td><td class=n>{money(o['payout'])}</td></tr>"
                for i, o in enumerate(cmp[p]))
            tax_note = ""
            if rt["fees"] != r["fees"]:
                tax_note = f"<p>If the buyer pays {TAX}% sales tax, {F['name']} charges its percentage on the tax too, so the fees rise to <b>{money(rt['fees'])}</b>.</p>"
            nearby = " · ".join(f"<a href='{url(f'how-much-does-{k}-take-from-{q}/')}'>${q}</a>" for q in PRICES if q != p)
            qa = [(f"How much does {F['name']} take from ${p}?",
                   f"{F['name']} takes {money(r['fees'])} from a ${p} sale with no shipping or sales tax, so you are paid {money(r['payout'])}. That's {r['feePct']}% of the sale.")]
            body = f"""<h1>How much does {esc(F['name'])} take from ${p}?</h1>
<div class=card><div class=note>On a ${p} sale {esc(F['name'])} takes</div><div class=big>{money(r['fees'])}</div>
<p>You're paid <b>{money(r['payout'])}</b>, which means {esc(F['name'])} keeps <b>{r['feePct']}%</b> of the sale. This assumes no shipping charged to the buyer, the standard category and no sales tax.</p>
<table><tbody>{lines}<tr><td><b>Total</b></td><td class=n><b>{money(r['fees'])}</b></td></tr></tbody></table></div>
{tax_note}
<p>Your real profit also depends on what you paid for the item and what shipping cost you. <a href="{url(F['slug'] + '/')}?price={p}">Run your exact numbers in the {esc(F['keyword'])}</a>.</p>
<h2>The same ${p} sale on other marketplaces</h2>
<div class=table-scroll><table><thead><tr><th>Platform</th><th class=n>Takes</th><th class=n>You get</th></tr></thead><tbody>{others}</tbody></table></div>
{cta()}
<p class=note>Other amounts: {nearby}</p>
<p class=note>Based on <a href="{esc(F['source'])}" rel="nofollow noopener" target="_blank">{esc(F['source_note'])}</a>, checked {CHECKED}.</p>"""
            page(path, title, desc, body, [faq_schema(qa)],
                 [("Home", ""), (F["keyword"], F["slug"] + "/"), (f"${p} sale", path)])

    # ---- home: compare
    qa = [
        ("Which marketplace has the lowest seller fees?", "It depends on the price. Depop (no US selling fee) and Mercari (flat 10%) usually leave you the most on everyday items, while Poshmark's 20% and flat $2.95 under $15 take the most. Use the calculator with your own price, shipping and cost."),
        ("Do fees apply to shipping and sales tax?", "On eBay, Depop, Etsy and Whatnot the payment or final value percentage is charged on a total that includes the tax the buyer pays. Mercari charges on item plus buyer-paid shipping. Poshmark charges on the sale price."),
        ("How often are the fees updated?", f"Each fee is checked against the platform's published fee page. Last check: {CHECKED}. A monitor watches those pages for changes."),
    ]
    links = "".join(f"<li><a href='{url(P[k]['slug'] + '/')}'>{esc(P[k]['keyword'])}</a></li>" for k in P)
    popular = " · ".join(f"<a href='{url(f'how-much-does-{k}-take-from-{p}/')}'>{P[k]['name']} ${p}</a>" for k in MARKETS for p in (20, 50, 100))
    desc = "Free seller fee calculator for eBay, Poshmark, Mercari, Depop, Etsy and Whatnot. Compare fees side by side and see where you keep the most profit."
    body = f"""<h1>Where do you keep the most money?</h1>
<p class=lede>Put in one sale and see what eBay, Poshmark, Mercari, Depop, Etsy and Whatnot each take, and what you actually profit. Free, no sign-up, fees checked {CHECKED}.</p>
{calc_block('compare', None, 'Your sale')}
<h2>Fee calculator for each marketplace</h2><ul class=grid-links>{links}</ul>
{cta()}
<h2>Quick answers</h2><p class=note>{popular}</p>
{faq_html(qa)}"""
    page("", f"Seller Fee Calculator {YEAR}: eBay, Poshmark, Mercari, Depop, Etsy, Whatnot", desc, body,
         [app_schema("PayoutMath seller fee calculator", "", desc), faq_schema(qa),
          {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": abs_url("")}])

    # ---- all fees table
    rows = "".join(f"<tr><td><a href='{url(P[k]['slug'] + '/')}'>{P[k]['name']}</a></td><td>{esc(P[k]['summary'])}</td>"
                   f"<td><a href='{esc(P[k]['source'])}' rel='nofollow noopener' target=_blank>Source</a></td></tr>" for k in P)
    page("marketplace-fees/", f"Marketplace seller fees {YEAR}: every platform in one table",
         f"eBay, Poshmark, Mercari, Depop, Etsy, Whatnot and PayPal seller fees for {YEAR} in one table, with the official source for each.",
         f"""<h1>Marketplace seller fees, {YEAR}</h1><p class=lede>Every fee {BRAND} uses, with where it came from. Last checked {CHECKED}.</p>
<div class=table-scroll><table><thead><tr><th>Platform</th><th>US seller fees</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class=note>Spotted a change before we did? Fees change without much notice. We re-check every source on a schedule.</p>""",
         crumbs=[("Home", ""), ("Marketplace fees", "marketplace-fees/")])

    # ---- profit tracker (lead magnet)
    csv = ("Date,Item,Platform,Sale price,Shipping charged,Platform fees,Item cost,Shipping paid,Profit,ROI %\n"
           + "".join(f",,,,,,,,=D{i}+E{i}-F{i}-G{i}-H{i},=IF(G{i}>0,I{i}/G{i}*100,\"\")\n" for i in range(2, 202)))
    (DIST / "reseller-profit-tracker.csv").write_text(csv)
    page("reseller-profit-tracker/", "Free reseller profit tracker spreadsheet (Google Sheets and Excel)",
         "Free reseller profit tracker template. Log every sale across eBay, Poshmark, Mercari and Depop and see profit and ROI automatically.",
         f"""<h1>Free reseller profit tracker</h1>
<p class=lede>A simple spreadsheet that works out profit and ROI for every sale, across every platform. Works in Google Sheets, Excel and Numbers.</p>
<div class=card><ol><li>Download the file.</li><li>In Google Sheets choose <b>File, Import, Upload</b> (or open it in Excel).</li><li>Fill in one row per sale. Get the fee from any {BRAND} calculator.</li></ol>
<a class=btn href="{url('reseller-profit-tracker.csv')}" download>Download the tracker</a></div>
{cta()}""", crumbs=[("Home", ""), ("Profit tracker", "reseller-profit-tracker/")])

    # ---- about / privacy / 404
    page("about/", f"About {BRAND}", f"{BRAND} is a free fee calculator for resellers.",
         f"""<h1>About {BRAND}</h1><p>{BRAND} is a free set of seller fee calculators for people who resell on eBay, Poshmark, Mercari, Depop, Etsy and Whatnot.</p>
<p>Every fee comes from the platform's own published fee page where one is available, and each page says where its numbers came from and when they were last checked. The math runs in your browser; nothing you type is sent anywhere.</p>
<p>{BRAND} isn't affiliated with any of the marketplaces it covers.</p>""", crumbs=[("Home", ""), ("About", "about/")])
    page("privacy/", f"Privacy policy | {BRAND}", f"How {BRAND} handles data.",
         f"""<h1>Privacy policy</h1><p>Last updated {CHECKED}.</p>
<p>The calculators run entirely in your browser. The numbers you enter aren't sent to us or stored on a server.</p>
<p>We may use privacy-friendly analytics to count page views, and in the future third-party advertising partners such as Google may use cookies to show ads. If that happens this page will be updated and you'll be able to opt out of personalised ads at Google's Ads Settings.</p>
<p>Some links are affiliate links. If you sign up through them we may earn a commission; the partner may set its own cookie to record the referral.</p>""",
         crumbs=[("Home", ""), ("Privacy", "privacy/")])
    (DIST / "404.html").write_text((DIST / "about/index.html").read_text().replace(
        f"<h1>About {BRAND}</h1>", f"<h1>Page not found</h1><p><a href='{url('')}'>Go to the fee calculator</a></p><h2>About {BRAND}</h2>", 1))

    # ---- sitemap / robots
    today = datetime.date.today().isoformat()
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in SITEMAP) + "</urlset>\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('sitemap.xml')}\n")
    print(f"Built {len(SITEMAP)} pages into {DIST}")

if __name__ == "__main__":
    build()
