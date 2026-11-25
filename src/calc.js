/* PayoutMath fee engine. Pure functions, no dependencies.
   Works in the browser (window.PM) and in Node (module.exports) so the
   build script and the pages use the exact same math. */
(function (root) {
  var r2 = function (n) { return Math.round((n + Number.EPSILON) * 100) / 100; };

  function tiered(amount, tiers) {
    // tiers: [[upTo|null, rate], ...]
    var fee = 0, prev = 0;
    for (var i = 0; i < tiers.length; i++) {
      var cap = tiers[i][0], rate = tiers[i][1];
      var top = cap === null ? amount : Math.min(amount, cap);
      if (top > prev) fee += (top - prev) * rate;
      if (cap === null || amount <= cap) break;
      prev = cap;
    }
    return fee;
  }

  // Each function returns {lines:[[label, amount]], fees, payout}
  // payout = money the platform pays you before your own costs.
  var fns = {
    ebay: function (F, x) {
      var c = F.categories[x.ebayCat] || F.categories.most;
      var total = x.price + x.ship + x.taxAmt;
      var fvf = tiered(total, c.tiers);
      var lines = [["Final value fee", fvf]];
      if (c.per_order) lines.push(["Per-order fee", total > 10 ? 0.40 : 0.30]);
      if (x.adRate > 0) lines.push(["Promoted listing ad fee (" + r2(x.adRate * 100) + "%)", total * x.adRate]);
      return lines;
    },
    poshmark: function (F, x) {
      var fee = x.price < F.flat_under ? F.flat_fee : x.price * F.rate;
      return [[x.price < F.flat_under ? "Flat fee (sale under $15)" : "20% commission", fee]];
    },
    mercari: function (F, x) {
      return [["10% selling fee", (x.price + x.ship) * F.rate]];
    },
    depop: function (F, x) {
      var total = x.price + x.ship + x.taxAmt;
      var lines = [["Payment processing (3.3% + $0.45)", total * F.proc_rate + F.proc_fixed]];
      if (x.boost) lines.push(["Boost fee (" + r2((x.boostRate || F.boost_default) * 100) + "%)", x.price * (x.boostRate || F.boost_default)]);
      return lines;
    },
    etsy: function (F, x) {
      var total = x.price + x.ship + x.taxAmt;
      var lines = [
        ["Listing fee", F.listing],
        ["Transaction fee (6.5%)", (x.price + x.ship) * F.txn_rate],
        ["Payment processing (3% + $0.25)", total * F.proc_rate + F.proc_fixed]
      ];
      if (x.offsite) {
        var rate = x.bigShop ? F.offsite_rate_big : F.offsite_rate;
        lines.push(["Offsite Ads (" + rate * 100 + "%)", Math.min((x.price + x.ship) * rate, F.offsite_cap)]);
      }
      return lines;
    },
    whatnot: function (F, x) {
      var c = F.categories[x.wnCat] || F.categories.most;
      var base = c.zero_above ? Math.min(x.price, c.zero_above) : x.price;
      var total = x.price + x.ship + x.taxAmt;
      return [
        ["Commission (" + c.rate * 100 + "%)", base * c.rate],
        ["Processing (2.9% + $0.30)", total * F.proc_rate + F.proc_fixed]
      ];
    },
    paypal: function (F, x) {
      var m = F.modes[x.ppMode] || F.modes.gs;
      var total = x.price + x.ship;
      var rate = m.rate + (x.intl ? F.intl : 0);
      return [["PayPal fee (" + r2(rate * 100) + "%" + (m.fixed ? " + $" + m.fixed.toFixed(2) : "") + ")", total * rate + m.fixed]];
    }
  };

  function norm(x) {
    var n = function (v) { v = parseFloat(v); return isFinite(v) && v > 0 ? v : 0; };
    var o = {};
    for (var k in x) o[k] = x[k];
    o.price = n(x.price); o.ship = n(x.ship); o.cost = n(x.cost);
    o.shipCost = n(x.shipCost); o.taxRate = n(x.taxRate) / 100;
    o.adRate = n(x.adRate) / 100; o.boostRate = x.boostRate ? n(x.boostRate) / 100 : 0;
    o.taxAmt = o.price * o.taxRate;
    return o;
  }

  function calc(FEES, key, input) {
    var x = norm(input);
    var F = FEES.platforms[key];
    // Poshmark buyers pay a prepaid label, so shipping never passes through the seller.
    if (key === "poshmark") { x.ship = 0; x.shipCost = 0; x.taxAmt = 0; }
    var lines = fns[key](F, x).map(function (l) { return [l[0], r2(l[1])]; });
    var fees = r2(lines.reduce(function (s, l) { return s + l[1]; }, 0));
    var payout = r2(x.price + x.ship - fees);
    var profit = r2(payout - x.cost - x.shipCost);
    var invested = x.cost + x.shipCost;
    return {
      key: key, name: F.name, lines: lines, fees: fees, payout: payout, profit: profit,
      feePct: x.price + x.ship > 0 ? r2(fees / (x.price + x.ship) * 100) : 0,
      margin: x.price + x.ship > 0 ? r2(profit / (x.price + x.ship) * 100) : 0,
      roi: x.cost > 0 ? r2(profit / x.cost * 100) : null,
      invested: r2(invested)
    };
  }

  // Lowest sale price that reaches a target profit (bisection; fees are monotonic in price).
  function priceFor(FEES, key, input, target) {
    var lo = 0, hi = 100000, base = {};
    for (var k in input) base[k] = input[k];
    for (var i = 0; i < 60; i++) {
      var mid = (lo + hi) / 2; base.price = mid;
      if (calc(FEES, key, base).profit >= target) hi = mid; else lo = mid;
    }
    return Math.ceil(hi * 100) / 100;
  }

  function compare(FEES, input, keys) {
    keys = keys || ["ebay", "poshmark", "mercari", "depop", "etsy", "whatnot"];
    return keys.map(function (k) { return calc(FEES, k, input); })
      .sort(function (a, b) { return b.profit - a.profit; });
  }

  var api = { calc: calc, priceFor: priceFor, compare: compare, r2: r2 };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PM = api;
})(this);
