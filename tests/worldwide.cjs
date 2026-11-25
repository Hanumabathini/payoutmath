const a=require('node:assert/strict'),world=require('../src/worldwide.js'),PM=require('../src/calc.js'),fees=require('../data/fees.json');
let rate={percent:3,fixed:0.25};
let x=world.estimate({mode:'etsy',price:100,ship:0,tax:0,cost:30,shipCost:0,listing:0.2,other:0,fx:false},rate);
a.ok(Math.abs(x.fees-9.95)<0.001);a.ok(Math.abs(x.profit-60.05)<0.001);
let y=world.estimate({mode:'custom',price:100,ship:0,tax:0,cost:20,shipCost:0,listing:0,other:0,commission:5,processing:2.5,fixed:0.3},null);
a.ok(Math.abs(y.fees-7.8)<0.001);a.ok(Math.abs(y.profit-72.2)<0.001);
let w=PM.calc(fees,'whatnot',{price:100,wnRate:'6',wnCat:'most'});a.equal(w.fees,9.2);
let defaultRate=PM.calc(fees,'whatnot',{price:100,wnCat:'most'});a.equal(defaultRate.fees,11.2);
console.log('PayoutMath global calculation tests passed.');
