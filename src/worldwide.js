/* PayoutMath worldwide — client-only estimator. No automatic FX or claims of eligibility. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.PMWorld=factory()})(this,function(){
'use strict';
function nonneg(v){var n=Number(v);return Number.isFinite(n)&&n>0?n:0}
function estimate(x,rate){var price=nonneg(x.price),ship=nonneg(x.ship),tax=nonneg(x.tax),cost=nonneg(x.cost),shipCost=nonneg(x.shipCost),listing=nonneg(x.listing),other=nonneg(x.other);var gross=price+ship,processed=gross+tax;var comm=0,proc=0,fx=0;
if(x.mode==='etsy'){if(!rate)return null;comm=gross*0.065;proc=processed*(rate.percent/100)+rate.fixed;fx=x.fx?gross*0.025:0;}
else{comm=gross*nonneg(x.commission)/100;proc=processed*nonneg(x.processing)/100+nonneg(x.fixed);}
var fees=comm+proc+fx+listing+other,payout=gross-fees,profit=payout-cost-shipCost;
return {gross,fees,payout,profit,margin:gross?100*profit/gross:0,lines:[['Commission / transaction',comm],['Processing',proc],['Currency conversion charge',fx],['Listing fee',listing],['Other charges',other]]}
}
function init(){var el=document.getElementById('worldwide');if(!el)return;var $=function(id){return document.getElementById('ww-'+id)};var data=null;
function money(v){var c=$('currency').value;try{return new Intl.NumberFormat('en',{style:'currency',currency:c,maximumFractionDigits:2}).format(v)}catch(_){return c+' '+v.toFixed(2)}}
function field(id){return $(id).value}
function render(){var mode=field('mode'),reg=data&&data.regions.find(function(r){return r.code===field('bank')});$('bank-wrap').hidden=mode!=='etsy';$('custom-fields').hidden=mode!=='custom';$('international-wrap').hidden=mode!=='etsy'||!reg||!reg.international;
if(mode==='etsy'&&reg&&$('currency').value!==reg.currency){$('status').textContent='The bank country uses '+reg.currency+'. Select that currency to avoid mixing currency amounts.';$('profit').textContent='—';return;}
var rate=reg&&$('international').checked&&reg.international?reg.international:reg&&reg.domestic;
var x={mode,price:field('price'),ship:field('ship'),tax:field('tax'),cost:field('cost'),shipCost:field('shipcost'),listing:field('listing'),other:field('other'),commission:field('commission'),processing:field('processing'),fixed:field('fixed'),fx:$('fx').checked};
if(mode==='etsy'&&!$('listing').value.trim()){ $('status').textContent='Enter the Etsy USD $0.20 listing fee converted into the selected bank currency using the actual rate from your payment account. No exchange rate is assumed.';$('profit').textContent='—';return;}
var r=estimate(x,rate);if(!r){$('status').textContent='Country rate unavailable. Use custom mode with verified rates.';return}
$('status').textContent=mode==='etsy'?'Etsy processing '+rate.percent+'% + '+money(rate.fixed)+'; separate 6.5% transaction fee.':'Custom fee rates entered by you; no marketplace-specific rates are implied.';
$('rate-note').textContent=mode==='etsy'?'Rates for '+reg.country+' sourced from Etsy Payments (bank-account country). VAT on fees, deposit charges and currency conversion may apply separately.':'For custom rates you are responsible for verifying the seller agreement for your region.';
$('profit').textContent=money(r.profit);$('profit').className='big '+(r.profit>=0?'pos':'neg');$('fees').textContent=money(r.fees);$('payout').textContent=money(r.payout);$('margin').textContent=r.margin.toFixed(1)+'%';
$('lines').textContent=r.lines.map(function(x){return x[0]+': '+money(x[1])}).join(' · ')
}
$('bank').addEventListener('change',function(){var r=data&&data.regions.find(function(t){return t.code===field('bank')});if(r){$('currency').value=r.currency;$('listing').value=r.currency==='USD'?'0.20':'';}render()});
$('mode').addEventListener('change',function(){if(field('mode')==='etsy'){var r=data&&data.regions.find(function(t){return t.code===field('bank')});if(r){$('currency').value=r.currency;$('listing').value=r.currency==='USD'?'0.20':''}}else $('listing').value='0';render()});
el.addEventListener('input',render);el.addEventListener('change',render);
fetch((function(){var path=location.pathname;return path.replace(/worldwide\/?$/,'etsy-country-rates.json')})()).then(function(r){if(!r.ok)throw Error('unavailable');return r.json()}).then(function(d){data=d;$('bank').value='US';$('currency').value='USD';$('listing').value='0.20';render()}).catch(function(){$('status').textContent='Country rate data failed to load. Choose custom mode and enter fees from your seller statement.';$('mode').value='custom';$('listing').value='0';render()});
}
if(typeof document!=='undefined'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()}
return {estimate};
});
