# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**Octopus Energy Dashboard** — a self-contained, client-side web app for UK Octopus
Energy customers. It reads a user's smart-meter data and the public Agile price feed
directly from the Octopus REST API and renders usage, costs, live half-hourly prices,
the cheapest upcoming times to use electricity, and an "would Agile save me money?"
backtest.

**Core principle: privacy.** Everything runs in the browser. The user's API key and
account number are stored only in `localStorage` and are sent only to
`api.octopus.energy`. There is no backend, no build step, no analytics, and nothing is
uploaded anywhere. Keep it that way — do not add servers, telemetry, bundlers, or
third-party data calls unless explicitly asked.

## Files

- `octopus-dashboard.html` — the entire app: HTML, CSS, and JS in one file. This is the
  product. Chart.js is the only external dependency, loaded from cdnjs.
- `octopus-proxy.py` — optional. A ~60-line stdlib-only local CORS proxy for the rare
  browser that blocks direct API calls. Not required in normal use.
- `README.md` — user-facing setup notes (create if missing).

There is no package.json, no node_modules, no framework. Resist adding them.

## Run / test

Open `octopus-dashboard.html` in a browser — that's it. There is no compile step.
For a quick local server: `python3 -m http.server` then visit the file.

Because there's no test runner, **always syntax-check the inline JS after edits**:

```bash
python3 -c "import re;open('/tmp/c.js','w').write('\n'.join(re.findall(r'<script>(.*?)</script>',open('octopus-dashboard.html').read(),re.S)))"
node --check /tmp/c.js
```

Use the **"Explore with sample data"** button (sets `DEMO=true`, served by the
`demoData()` function) to exercise the whole UI without real credentials. When you add a
feature that calls a new endpoint, add a matching branch to `demoData()` so demo mode
keeps working.

## Architecture

Single-page app, no router. Flow:

1. `DOMContentLoaded` → if `localStorage` has creds, call `boot()`; else show `#splash`.
2. `boot()` → `loadAccount()` discovers meters/tariffs/region, then `renderOverview()`.
3. Tab clicks → `showView(v)`; each view renders lazily once (tracked in the `rendered`
   object) and caches results on `state`.

Key globals:

- `LS` — typed getters/setters over `localStorage` (`octo_key`, `octo_acct`, `octo_base`).
- `state` — runtime data: `account`, `elec`, `gas`, `exp`, `agile`, `region`, `charts`,
  plus per-view caches.
- `rendered` — which views have already drawn. **Declared with `let`** because `boot()`
  resets it via `rendered = {}` (see Gotchas).
- `DEMO` — when true, `api()` is short-circuited to `demoData()`.

Data access helpers:

- `api(path, params)` — single request. Adds `Authorization: Basic base64(key + ":")`,
  maps 401/403 to a friendly AUTH error and network failures to a CORS hint.
- `apiAll(path, params, maxPages)` — follows the `next` pagination link, capped.

## Octopus API notes (important domain knowledge)

Base URL `https://api.octopus.energy/v1/`. Auth is HTTP Basic: **API key as username,
empty password**. Product/price endpoints are public (no auth); account and consumption
endpoints require the key. Datetimes are ISO 8601; always send `Z` (UTC) to avoid
DST bugs.

Endpoints in use:

- `accounts/{acct}/` — meters (MPAN/MPRN + serials), `is_export` flag, and tariff
  `agreements` history.
- `electricity-meter-points/{mpan}/meters/{serial}/consumption/` — half-hourly kWh.
  Use `page_size=25000`, `order_by=period`, and explicit `period_from`/`period_to`.
  Gas is the same under `gas-meter-points/{mprn}/...`. Export reads back as
  "consumption" on the export MPAN.
- `products/` — discovery; filter `brand=OCTOPUS_ENERGY`. The current Agile import
  product is found dynamically (code starts with `AGILE`, `direction==='IMPORT'`,
  `available_to===null`, newest `available_from`). **Do not hardcode the Agile product
  code** — it changes over time.
- `products/{product}/electricity-tariffs/{tariffCode}/standard-unit-rates/` and
  `.../standing-charges/` — prices. VAT-inclusive value is `value_inc_vat`.

Tariff codes look like `E-1R-AGILE-FLEX-22-11-25-C`:
- Last segment = **region** letter (A–P, GSP group).
- Second segment = register count: `1R` single, `2R` Economy 7.
- Middle = **product code** (`AGILE-FLEX-22-11-25`).

`parseTariffCode()` returns `{region, registers, product, code}`. Any object passed to
`getUnitRates()` / `getStandingCharge()` MUST expose `.product` and `.code` — keep that
shape consistent across `state.elec.tariff`, `state.gas.tariff`, and `state.agile`.

## Conventions

- **One file.** New features go inside `octopus-dashboard.html`. Don't split it.
- **No frameworks / no localStorage-breaking patterns.** Vanilla DOM + Chart.js only.
- CSS uses the variables defined in `:root` (Octopus pink `--accent`, teal, etc.). Reuse
  `.panel`, `.card`, `.grid.cards`, `.slotcard`, `.status` rather than new ad-hoc styles.
- Render a view by: clear/loading state → fetch via `api`/`apiAll` → build cards with the
  `card()` helper → draw charts with `mkChart(id, cfg)` (it destroys the old chart first).
- Money in `£` via `fmtGBP`, prices in `p` via `fmtP`, energy via `fmtKWh`. Prices are
  p/kWh; divide by 100 before multiplying kWh to get £.
- Always wrap view renders in try/catch and surface errors through `setStatus(...,'err')`.
- Keep demo data (`demoData()`) in sync with any new endpoint.

## Gotchas (bugs already fixed — don't reintroduce)

- **`const` reassignment.** `rendered` must be `let`; reassigning a `const` throws
  "Attempted to assign to readonly property" in Safari and aborts boot.
- **Tariff object field names.** `state.agile` stores the tariff string under `.code`
  (not `.tariff`); `getUnitRates`/`getStandingCharge` read `.code` and `.product`.
- **DST.** Send UTC `Z` on every `period_from`/`period_to`.
- **Economy 7 (`2R`).** Cost calc approximates a night window of 00:30–07:30 local
  unless separate registers are reported; note this in any cost UI.

## Roadmap ideas (when asked)

EV / appliance smart-charge schedule export (iCal/JSON), carbon-intensity overlay
(carbonintensity.org.uk), daily "cheap window" notification, CSV export of consumption,
Octopus Go / Intelligent Go / Cosy comparison, multi-property support.

## Git

Use clear, scoped commits (e.g. `fix: align agile tariff field with rate fetchers`).
Never commit a real API key or account number — `.gitignore` any local creds/cache files
and keep sample data fictional.
