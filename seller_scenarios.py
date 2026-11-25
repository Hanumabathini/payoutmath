"""Separate seller costs estimator: user-entered rates, no invented regional fees."""
import shutil
def build_seller_scenarios(page,url,ROOT,DIST,checked):
    shutil.copy(ROOT/"src/selling-costs.js",DIST/"selling-costs.js")
    body='''<h1>Every cost between the sale and your bank.</h1>
<p class="lede">Compare a buyer-paid-shipping offer with free shipping, including packaging, discounts, and a configurable return reserve. Enter the actual commission and processing fee from your marketplace statement.</p>
<div class="warn" style="background:#e5eee9;color:#163e34;padding:15px 17px;border-radius:12px;border:1px solid #bcd8cb;margin:20px 0"><strong>Scenario planning, not a fee quote.</strong> All rates below are your inputs. Marketplace-specific fee bases, buyer fees, refunds, tax/VAT, shipping carrier pricing and discounted labels can differ. No marketplace or regional rate is assumed.</div>
<section class="calc" id="selling-costs">
<div class="card"><h2 style="margin-top:0">Sale assumptions</h2>
<div class="fields">
<div class="full"><label for="sc-cur">All amounts in</label><select id="sc-cur"><option>USD</option><option>GBP</option><option>EUR</option><option>CAD</option><option>AUD</option><option>INR</option><option>JPY</option><option>BRL</option><option>MXN</option><option>SGD</option><option>AED</option><option>Other</option></select></div>
<div><label for="sc-price">Listed item price</label><input id="sc-price" type="number" min="0" step=".01" value="50"></div>
<div><label for="sc-cost">Cost of the item</label><input id="sc-cost" type="number" min="0" step=".01" value="15"></div>
<div><label for="sc-shipping">Buyer-paid shipping in offer A</label><input id="sc-shipping" type="number" min="0" step=".01" value="7"></div>
<div><label for="sc-label">Actual shipping-label cost</label><input id="sc-label" type="number" min="0" step=".01" value="7"></div>
<div><label for="sc-packaging">Packaging and supplies</label><input id="sc-packaging" type="number" min="0" step=".01" value="1"></div>
<div><label for="sc-discount">Discount / coupon paid by seller</label><input id="sc-discount" type="number" min="0" step=".01" value="0"></div>
<div><label for="sc-commission">Marketplace commission (%)</label><input id="sc-commission" type="number" min="0" max="100" step=".01" value="0"></div>
<div><label for="sc-processing">Payment-processing rate (%)</label><input id="sc-processing" type="number" min="0" max="100" step=".01" value="0"></div>
<div><label for="sc-fixed">Fixed marketplace/processing fee</label><input id="sc-fixed" type="number" min="0" step=".01" value="0"></div>
<div><label for="sc-tax">Buyer sales tax in processing base</label><input id="sc-tax" type="number" min="0" step=".01" value="0"></div>
<div><label for="sc-other">Advertising, listing and other charges</label><input id="sc-other" type="number" min="0" step=".01" value="0"></div>
<div><label for="sc-reserve">Reserve for expected refund/return losses (%)</label><input id="sc-reserve" type="number" min="0" max="100" step=".1" value="0"></div>
</div><p class="note">Fee base here: marketplace percentage of discounted item plus buyer-paid shipping, processing percentage of that amount plus tax. If your marketplace uses different fee bases, use the platform calculator or actual statement instead.</p></div>
<div class="card" aria-live="polite"><h2 style="margin-top:0">Two shipping offers</h2>
<p class="note">A. Buyer pays the shipping amount you enter. B. You offer free shipping at the same item price.</p>
<div class="kpis"><div class="kpi"><small>Buyer pays shipping</small><b id="sc-profitA">—</b></div><div class="kpi"><small>Free shipping</small><b id="sc-profitB">—</b></div><div class="kpi"><small>Difference</small><b id="sc-difference">—</b></div></div>
<div id="sc-details" class="note"></div><p class="note">Profit after a return-loss reserve is not a realized result. Reserves are optional estimates chosen by you.</p></div>
</section>
<h2>What this includes</h2><p>Marketplace commission, payment processing, shipping label, packaging, seller discount, optional other charges and your specified loss reserve. This is a scenario tool—not a claim that each marketplace treats tax, shipping or returns identically.</p>
<h2>Learn the actual platform fees</h2><p><a href="'''+url("marketplace-fees/")+'''">Read the U.S. sources and base fee models</a> or use the <a href="'''+url("worldwide/")+'''">worldwide calculator</a> for verified country-specific Etsy processing and manual fee entry.</p>
<script src="'''+url("selling-costs.js")+'''"></script>'''
    page("selling-costs/","Shipping, packaging and return-cost profit planner | PayoutMath","Compare reseller profit after shipping, packaging, marketplace fees, discounts and a chosen return reserve. Enter actual rates; no fabricated fees.",body,crumbs=[("Home",""),("Selling costs","selling-costs/")])
