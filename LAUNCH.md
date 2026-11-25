# PayoutMath launch guide

PayoutMath is a free fee and profit calculator site for people who resell on eBay, Poshmark, Mercari, Depop, Etsy, Whatnot and PayPal. It is finished and tested. Everything below costs $0.

Only four steps need you, because each one needs your own account. Do them in order. Each takes about 5 to 10 minutes.

## Step 1. Put the site online (GitHub Pages, free)

The code is already in your public `payoutmath` repository, and it's set up for `https://hanumabathini.github.io/payoutmath/`.

1. In the repository, open **Settings > Pages** and set **Source** to **GitHub Actions**.
2. Open the **Actions** tab, pick **Deploy site**, and press **Run workflow**. About two minutes later the site is live at `https://hanumabathini.github.io/payoutmath/`.

If you later buy your own domain, add two repository variables (**Settings > Secrets and variables > Actions > Variables**): `SITE_URL` set to the domain, like `https://payoutmath.com`, and `BASE_PATH` set to `/`.

## Step 2. Set up how you get paid (Crosslist affiliate)

This is the payout account. The site's buttons send resellers to Crosslist, a tool that copies one listing to every marketplace.

- **Where:** affiliate.crosslist.com. Crosslist says approval is instant and anyone can join.
- **What you earn:** 25% of what each referred customer pays, every month for their first 6 months. Their cookie lasts 60 days.
- **How you get paid:** monthly, around the 20th, once you pass $50. Crosslist pays through a service called Dots, which sends it to your **PayPal or bank account**. Pick PayPal if you already have one, because it is the quickest to set up.
- **Rules to keep:** no paid ads, no coupon sites, no spam. The site follows these already.

When you have your affiliate link, add one more repository variable, `CROSSLIST_URL`, set to that link, then run **Deploy site** again. Every button on every page switches to your link.

## Step 3. Tell Google and Bing the site exists (free)

1. Go to Google Search Console, add the site as a **URL prefix** property (`https://hanumabathini.github.io/payoutmath/`) and choose the **HTML tag** method.
2. Copy only the long code inside `content="..."` and save it as a repository variable named `GSC_TOKEN`. Run **Deploy site** again, then press **Verify** in Search Console.
3. In Search Console, open **Sitemaps** and submit `sitemap.xml`.
4. In Bing Webmaster Tools, choose **Import from Google Search Console**. That covers Bing, DuckDuckGo and Yahoo.

## Step 4 (later, optional). Ads, once there is traffic

Ad networks such as Google AdSense will not accept a `github.io` address. When the site gets about 100 visitors a day, buy a domain (about $10 a year), point it at the site, and apply to AdSense. Until then, Crosslist is the income.

## What runs by itself after launch

- **Deploy site** rebuilds and republishes whenever anything in the repository changes.
- **Fee check** runs every Monday. It reads each marketplace's official fee page and opens an issue in your repository if a fee the site relies on seems to have changed. It never changes the numbers by itself, so a wrong reading can't break the site. Some marketplaces block automated checks; those show up as "could not reach" and don't open an issue on their own.
- When an issue opens, send it to me and I'll check the new fee and update `data/fees.json`.

## Files

- `data/fees.json` holds every fee rule with its source link and the date it was checked.
- `src/calc.js` is the one fee engine. The live calculators and the built pages both use it, so their numbers always match.
- `build.py` builds the 72 pages into `dist/` (`python3 build.py`, needs Python 3 and Node).
- `scripts/check_fees.py` is the weekly fee check.
