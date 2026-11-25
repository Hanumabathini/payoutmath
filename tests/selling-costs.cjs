const a=require('node:assert/strict'),s=require('../src/selling-costs.js');
let x={price:50,cost:15,shipping:7,label:7,packaging:1,discount:0,commission:10,processing:3,fixed:0.25,tax:0,other:0,reserve:0};
let q=s.calculate(x,false),r=s.calculate(x,true);
a.ok(Math.abs(q.profit-26.34)<1e-6);a.ok(Math.abs(r.profit-20.25)<1e-6);
a.equal(s.calculate({...x,reserve:10},false).reserve,5.7);
console.log('Seller scenario tests passed');
