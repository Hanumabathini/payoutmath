"""Worldwide reseller net-profit worksheet. Rates are only prefilled where the named official source publishes them."""
import json, shutil
def build_worldwide(page,url,ROOT,DIST,checked):
    shutil.copy(ROOT/"src/worldwide.js",DIST/"worldwide.js")
    (DIST/"etsy-country-rates.json").write_text((ROOT/"data/etsy-country-rates.json").read_text())
    options = "".join('<option value="'+r["code"]+'">'+r["country"]+' — '+r["currency"]+'</option>' for r in json.loads((ROOT/"data/etsy-country-rates.json").read_text())["regions"])
    body='''<h1>Know your profit. In your currency.</h1>
<p class="lede">A transparent worldwide seller-profit worksheet. Choose an official Etsy Payments bank-country rate, or enter the actual fee rates from any other marketplace. Nothing is converted using a made-up exchange rate.</p>
<div class="warn" style="background:#e5eee9;color:#173c34;border:1px solid #b8d2c7;padding:16px;border-radius:12px;margin:24px 0"><strong>Source-backed, not universal.</strong> Etsy's 6.5% transaction fee is separate from its bank-country payment-processing fee. Other marketplace and country combinations require your own fee statement. Currency conversion, tax, VAT on fees, deposits, subscriptions, advertising and returns may add charges. Last source review: '''+checked+'''.</div>
<section class="calc" id="worldwide">
<div class="card"><h2 style="margin-top:0">Your sale</h2><div class="fields">
<div class="full"><label for="ww-mode">Calculation model</label><select id="ww-mode"><option value="etsy">Etsy — published bank-country rates</option><option value="custom">Other marketplace — enter your fees manually</option></select></div>
<div class="full" id="ww-bank-wrap"><label for="ww-bank">Location of your Etsy Payments bank account</label><select id="ww-bank">'''+options+'''</select></div>
<div class="full"><label for="ww-currency">Currency for all amounts entered below</label><select id="ww-currency"><option>USD</option><option>GBP</option><option>CAD</option><option>AUD</option><option>EUR</option><option>INR</option><option>JPY</option><option>NZD</option><option>CHF</option><option>SGD</option><option>HKD</option><option>SEK</option><option>NOK</option><option>DKK</option><option>MXN</option><option>ZAR</option><option>MYR</option><option>PHP</option><option>IDR</option><option>TRY</option><option>ILS</option><option>VND</option><option>AED</option><option>KRW</option><option>BRL</option></select></div>
<div id="ww-international-wrap" class="full"><label class="check"><input id="ww-international" type="checkbox"> International order (where bank-country rate differs)</label></div>
<div><label for="ww-price">Item sale price</label><input type="number" id="ww-price" min="0" step=".01" value="100"></div>
<div><label for="ww-ship">Shipping charged to buyer</label><input type="number" id="ww-ship" min="0" step=".01" value="0"></div>
<div><label for="ww-tax">Sales tax collected (affects processing base)</label><input type="number" id="ww-tax" min="0" step=".01" value="0"></div>
<div><label for="ww-cost">Your item cost</label><input type="number" id="ww-cost" min="0" step=".01" value="30"></div>
<div><label for="ww-shipcost">Your actual shipping cost</label><input type="number" id="ww-shipcost" min="0" step=".01" value="0"></div>
<div><label for="ww-listing">Listing charge in selected currency</label><input type="number" id="ww-listing" min="0" step=".01" placeholder="Enter exact local-currency charge"></div>
<div id="ww-custom-fields" class="full" hidden><div class="fields">
<div><label for="ww-commission">Marketplace commission (%)</label><input type="number" id="ww-commission" min="0" max="100" step=".01" value="0"></div>
<div><label for="ww-processing">Payment processing (%)</label><input type="number" id="ww-processing" min="0" max="100" step=".01" value="0"></div>
<div><label for="ww-fixed">Fixed processing charge</label><input type="number" id="ww-fixed" min="0" step=".01" value="0"></div></div></div>
<div class="full"><label for="ww-other">Other real charges (ads, VAT on fees, deposits etc.)</label><input type="number" id="ww-other" min="0" step=".01" value="0"></div>
<div class="full"><label class="check"><input type="checkbox" id="ww-fx"> Etsy converts listing currency to payout account currency (2.5% model charge)</label></div>
</div><p id="ww-rate-note" class="note"></p></div>
<div class="card" aria-live="polite"><p class="note" id="ww-status"></p><h2 style="margin-top:0">Estimated net profit</h2><div class="big" id="ww-profit">—</div><div class="kpis"><div class="kpi"><small>Modeled fees</small><b id="ww-fees">—</b></div><div class="kpi"><small>Seller payout</small><b id="ww-payout">—</b></div><div class="kpi"><small>Margin</small><b id="ww-margin">—</b></div></div><div id="ww-lines" class="note"></div><p class="note">All inputs are calculated locally. No automatic FX conversion; all numeric amounts must be in the selected currency. This is an estimate, not an invoice.</p></div>
</section>
<h2>Where do these rates come from?</h2><p><a target="_blank" rel="noopener" href="https://help.etsy.com/hc/en-us/articles/115015628847-What-are-Payment-Processing-Fees-for-Selling-on-Etsy">Etsy official processing fees by bank country</a> · <a target="_blank" rel="noopener" href="https://www.etsy.com/legal/fees/">Etsy fee policy</a>. Published country-specific amounts may change; rates are reviewed manually rather than invented.</p>
<h2>Other marketplace or unsupported country?</h2><p>Choose the manual mode and enter the fee percentages, fixed charge and listing cost shown in your platform account. Until a regional rate is independently verified, PayoutMath will not substitute US marketplace percentages.</p>
<script src="'''+url("worldwide.js")+'''"></script>'''
    page("worldwide/","Worldwide seller fee and profit calculator | PayoutMath","Calculate reseller profit in local currencies. Official Etsy processing fees for selected bank countries and transparent manual fees for other markets.",body,crumbs=[("Home",""),("Worldwide","worldwide/")])
