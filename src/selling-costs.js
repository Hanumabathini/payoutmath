/* Seller profit scenarios — no regional fee assumptions. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.SellingCosts=factory()})(this,function(){
'use strict';function n(v){var x=Number(v);return Number.isFinite(x)&&x>=0?x:0}
function calculate(x,freeShipping){var price=n(x.price),discount=Math.min(price,n(x.discount)),ship=freeShipping?0:n(x.shipping),sale=price-discount+ship;
var commission=sale*n(x.commission)/100,process=(sale+n(x.tax))*n(x.processing)/100,fees=commission+process+n(x.fixed)+n(x.other);
var reserve=sale*n(x.reserve)/100,profit=sale-fees-n(x.cost)-n(x.label)-n(x.packaging)-reserve;
return {sale,fees,commission,process,reserve,profit,payout:sale-fees,margin:sale>0?100*profit/sale:0};
}
function init(){var el=document.getElementById('selling-costs');if(!el)return;var $=id=>document.getElementById('sc-'+id);
function money(n){let c=$('cur').value;try{return new Intl.NumberFormat('en',{style:'currency',currency:c,maximumFractionDigits:2}).format(n)}catch(e){return c+' '+n.toFixed(2)}}
function render(){let x={};for(let k of ['price','cost','shipping','label','packaging','discount','commission','processing','fixed','tax','other','reserve'])x[k]=$(k).value;
let a=calculate(x,false),b=calculate(x,true);$('profitA').textContent=money(a.profit);$('profitB').textContent=money(b.profit);$('difference').textContent=money(a.profit-b.profit);
$('details').textContent='Buyer-paid offer: modeled fees '+money(a.fees)+', packaging '+money(n(x.packaging))+', shipping label '+money(n(x.label))+', return reserve '+money(a.reserve)+'. Free-shipping offer: modeled fees '+money(b.fees)+', profit margin '+b.margin.toFixed(1)+'%. All terms are estimates.';
}
el.addEventListener('input',render);el.addEventListener('change',render);render()}
if(typeof document!=='undefined'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()}return {calculate};
});
