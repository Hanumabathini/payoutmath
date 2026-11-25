# PayoutMath

Free fee and profit calculators for resellers on eBay, Poshmark, Mercari, Depop, Etsy, Whatnot and PayPal, plus prop firm tools for funded futures traders (Topstep, Tradeify, MyFundedFutures).

- `python3 build.py` builds the static site into `dist/` (needs Python 3 and Node).
- Pushing to `main` deploys to GitHub Pages (`.github/workflows/deploy.yml`).
- Every Monday, `.github/workflows/fee-check.yml` checks each platform's fee page and opens an issue if a fee seems to have changed.
- Setup steps are in `LAUNCH.md`.
