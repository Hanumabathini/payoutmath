/* PayoutMath page wiring. Reads inputs, runs PM.calc, renders results. */
(function () {
  var root = document.getElementById("pm");
  if (!root || !window.PM || !window.FEES) return;
  var mode = root.getAttribute("data-mode");          // "single" | "compare"
  var key = root.getAttribute("data-platform");        // for single
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return (n < 0 ? "-$" : "$") + Math.abs(n).toFixed(2); };
  var fields = ["price", "ship", "shipCost", "cost", "taxRate", "adRate", "boostRate", "target"];
  var checks = ["boost", "offsite", "bigShop", "intl"];
  var selects = ["ebayCat", "wnCat", "ppMode"];

  // Restore from URL so results can be shared.
  try {
    var q = new URLSearchParams(location.search);
    fields.concat(selects).forEach(function (f) { if (q.has(f) && $(f)) $(f).value = q.get(f); });
    checks.forEach(function (f) { if (q.get(f) === "1" && $(f)) $(f).checked = true; });
  } catch (e) {}

  function read() {
    var x = {};
    fields.concat(selects).forEach(function (f) { if ($(f)) x[f] = $(f).value; });
    checks.forEach(function (f) { if ($(f)) x[f] = $(f).checked; });
    return x;
  }

  function single(x) {
    var r = PM.calc(FEES, key, x);
    var rows = r.lines.map(function (l) { return "<tr><td>" + l[0] + "</td><td class=n>" + money(l[1]) + "</td></tr>"; }).join("");
    var out = "<div class=note>Your profit</div><div class='big " + (r.profit >= 0 ? "pos" : "neg") + "'>" + money(r.profit) + "</div>" +
      "<div class=kpis><div class=kpi><small>" + FEES.platforms[key].name + " takes</small><b>" + money(r.fees) + "</b></div>" +
      "<div class=kpi><small>Payout to you</small><b>" + money(r.payout) + "</b></div>" +
      "<div class=kpi><small>" + (r.roi === null ? "Margin" : "ROI") + "</small><b>" + (r.roi === null ? r.margin : r.roi) + "%</b></div></div>" +
      "<table><tbody>" + rows + "<tr><td><b>Total fees (" + r.feePct + "% of the sale)</b></td><td class=n><b>" + money(r.fees) + "</b></td></tr></tbody></table>";
    var t = parseFloat(x.target);
    if (isFinite(t) && $("reverse")) {
      $("reverse").innerHTML = "To make <b>" + money(t) + "</b> profit, list at <b>" + money(PM.priceFor(FEES, key, x, t)) + "</b> or more.";
    }
    return out;
  }

  function compare(x) {
    var list = PM.compare(FEES, x);
    var rows = list.map(function (r, i) {
      return "<tr" + (i === 0 ? " class=rank1" : "") + "><td><a href='" + root.getAttribute("data-base") + "/" + FEES.platforms[r.key].slug + "/'>" + r.name + "</a>" + (i === 0 ? "<span class=pill>Best</span>" : "") +
        "</td><td class=n>" + money(r.fees) + "</td><td class=n>" + money(r.payout) + "</td><td class='n " + (r.profit >= 0 ? "pos" : "neg") + "'>" + money(r.profit) + "</td></tr>";
    }).join("");
    var best = list[0], worst = list[list.length - 1];
    return "<div class=note>You keep the most on</div><div class='big pos'>" + best.name + "</div>" +
      "<p class=note>" + money(r2(best.profit - worst.profit)) + " more than on " + worst.name + " for this sale.</p>" +
      "<div class=table-scroll><table><thead><tr><th>Platform</th><th class=n>Fees</th><th class=n>Payout</th><th class=n>Profit</th></tr></thead><tbody>" + rows + "</tbody></table></div>";
  }
  var r2 = PM.r2;

  function run() {
    var x = read();
    $("result").innerHTML = mode === "compare" ? compare(x) : single(x);
    try {
      var q = new URLSearchParams();
      fields.concat(selects).forEach(function (f) { if ($(f) && $(f).value !== "") q.set(f, $(f).value); });
      checks.forEach(function (f) { if ($(f) && $(f).checked) q.set(f, "1"); });
      history.replaceState(null, "", "?" + q.toString());
    } catch (e) {}
  }
  root.addEventListener("input", run);
  root.addEventListener("change", run);
  run();
})();
