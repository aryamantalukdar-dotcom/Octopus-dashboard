# 🐙 Octopus Energy Dashboard

A self-contained, client-side dashboard for UK Octopus Energy customers. It reads your
smart-meter data and the public Agile price feed straight from the Octopus REST API and
shows:

- **Overview** — your tariff, region, current unit rate, standing charge, and the last
  week at a glance.
- **Usage** — daily kWh for the last 30 days, your average day profile (find your
  peaks!), and one-click **CSV export** of half-hourly readings.
- **Costs** — daily £ reconstructed from half-hourly usage × your tariff's historic
  rates, plus a naive annual projection.
- **Agile prices** — today's (and, after ~16:00, tomorrow's) live half-hourly Agile
  prices for your region.
- **Cheap slots** — the cheapest upcoming 1/2/3/4-hour windows to run appliances.
- **Agile savings** — a 30-day backtest: *would Agile have been cheaper than your
  current tariff for the way you actually use electricity?* Great if you're on the
  standard (Flexible) tariff and Agile-curious.

## 🔒 Privacy

Everything runs in your browser. Your API key and account number live only in your
browser's `localStorage` and are sent only to `api.octopus.energy`. There is no backend,
no build step, no analytics, and nothing is uploaded anywhere.

> Hosting note: GitHub Pages serves the static HTML file; it never sees your key —
> all API calls go from your browser directly to Octopus.

## Use it

**Hosted (after enabling GitHub Pages):**
https://aryamantalukdar-dotcom.github.io/Octopus-dashboard/

**Locally:** just open `octopus-dashboard.html` in a browser. Or serve it:

```bash
python3 -m http.server
# then visit http://localhost:8000/octopus-dashboard.html
```

You'll need:

1. Your **API key** — from
   [octopus.energy → Personal details → API access](https://octopus.energy/dashboard/new/accounts/personal-details/api-access)
   (starts `sk_live_`).
2. Your **account number** — top of your Octopus dashboard, looks like `A-1234ABCD`.

No account? Hit **"Explore with sample data"** to try the whole UI with realistic
fictional data.

### If charts load but data doesn't (CORS)

The Octopus API allows direct browser calls in all mainstream browsers. If yours blocks
them, run the bundled stdlib-only proxy and point the dashboard at it:

```bash
python3 octopus-proxy.py
# then set "API base URL" (Advanced, on the connect screen) to http://localhost:8001/v1/
```

## Deploying / hosting

The repo ships with a GitHub Actions workflow (`.github/workflows/deploy-pages.yml`)
that publishes the dashboard to GitHub Pages on every push to `main` (it copies
`octopus-dashboard.html` to `index.html` at deploy time). The first run enables Pages
automatically. You can also trigger it manually from the Actions tab.

## Notes & limitations

- Prices shown include VAT. Costs are reconstructed from half-hourly data and may
  differ slightly from your bill (rounding, estimated reads).
- Smart-meter consumption usually lags 24–48 hours, and requires half-hourly
  reporting to be enabled on your meter.
- Economy 7: the night window is approximated as 00:30–07:30 local time.
- Tomorrow's Agile prices are published around 16:00 UK time.
- Unofficial tool — not affiliated with Octopus Energy.
