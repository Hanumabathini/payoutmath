# Competitor-informed improvement notes — PayoutMath (25 Nov 2026)

Analyzed live, publicly indexed calculators without copying their content or designs.
- KeptProfit (https://keptprofit.com/): fields for shipping method, package weight, packaging, categories, Whatnot tiers, buyer cost, and profit breakdown. PayoutMath now has explicit shipping/packaging/return scenario inputs but **not** an unverified USPS estimate.
- FlipperTools (https://flippertools.com/tools/reseller-profit-calculator): multi-platform profit comparison with shareable results. PayoutMath already has a US comparison and URL-based share state. Our new page focuses on cost transparency instead.
- ResellFees (https://resellfees.com/compare/): pairwise US comparisons; PayoutMath's global worksheet avoids falsely extending US rates internationally.
- MarginOS (https://margin.byna.me/): actual payout statement reconciliation; not implemented until a secure consent-based upload and settlement parser can be built.

**Accuracy boundaries:** No global eBay rate is inferred; no regional USPS shipping cost is fabricated; no marketplace buyer-fee formula is assumed. Sellers must use rates from their own accounts when region and category are not verified. Treat illustrative commission results as estimates.

Critical next releases: reconciled returns/refunds by marketplace, approved category-country matrix, platform-specific payment fee bases, and more country processing data directly sourced from marketplace help. Affiliate revenue is inactive pending approval and referral URLs.
