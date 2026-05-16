# Testing `farm_quickbooks_io` end-to-end

Two paths depending on what you want to test:

## Path A — stub mode (no Intuit account needed)

The module ships with a deterministic fixture so the full UI flow is demo-able without
real Intuit credentials:

1. Install `farm_quickbooks_io` (or `farm_pack_demo` which preloads a stub-mode
   connection)
2. Farm → QuickBooks → Connections → open the sandbox connection
3. Farm → QuickBooks → Start New Import → Start Import
4. You'll see ~10 mapping rows (5 accounts, 2 vendors, 2 customers, 3 products) on the
   resulting import in `review` state
5. Click **Commit** — the accounts/partners/products materialize into Odoo
6. Click **Rollback** to reverse the commit

Stub mode is enough for partner demos and validating the UX.

## Path B — real QuickBooks Online (round-trip with your data)

This is the path described in the original question: _sign up for QBO → create a farm
there → convert it over to Odoo._

### B1. Create an Intuit Developer account (free)

1. Go to https://developer.intuit.com
2. Sign in with an Intuit ID (create one if you don't have it — the same ID can be used
   for your own QBO subscription later)
3. Visit **My Apps** → **Create an app** → choose **QuickBooks Online and Payments**
4. Pick a name (e.g. "Farm Pack Connector")
5. On the app page, **Keys & OAuth** tab → you now have separate **Development** and
   **Production** keys. For testing use Development.

### B2. Configure the redirect URI

On the same Keys & OAuth tab, add a Redirect URI:

```
https://<your-host>/farm_qbo/oauth/callback
```

For local development with the `deploy/` docker-compose recipe, this is
`http://localhost:8069/farm_qbo/oauth/callback`. **Intuit requires HTTPS for
production** — use ngrok or a real cert for non-localhost testing.

### B3. Set credentials in Odoo

1. In Odoo: **Settings → QuickBooks (Farm Pack)** (or
   `/web#action=farm_quickbooks_io.action_farm_qbo_settings`)
2. Paste **Client ID**, **Client Secret**, and the same **Redirect URI** from step B2
3. **Save**

### B4. Create or pick a QBO sandbox company

Two options:

**Sandbox** (free, lives forever): on the Intuit Developer dashboard, **Sandbox**
section → **Add a sandbox company** → "Sandbox 1" is sufficient. Sandbox companies come
pre-populated with realistic transactions you can convert.

**Real QBO trial**: sign up for a 30-day trial at https://quickbooks.intuit.com. Then
**create a farm there** — set up:

- A chart of accounts with farm categories (Sales of Eggs, Sales of Produce, Feed
  Purchased, Fuel, Seeds, Fertilizer, etc.)
- A few vendors (feed co-op, tractor supply)
- A few customers (CSA members, wellness pantry)
- A few products (eggs dozen, salad greens, herb bundle)
- ~3 months of sample transactions

This is the realistic dry-run for what an actual farmer's migration will look like.

### B5. Connect from Odoo

1. **Farm → QuickBooks → Connections** → new record (or open the demo one); set
   **Environment** to Sandbox (or Production for a trial QBO)
2. Click **Connect QuickBooks** → opens Intuit's OAuth prompt
3. Pick the sandbox/trial company → click **Connect**
4. Intuit redirects back to `/farm_qbo/oauth/callback`; the connection's `realm_id`,
   `access_token`, `refresh_token`, and `token_expires_at` are populated. State flips to
   **Connected**.

### B6. Run an import

1. **Farm → QuickBooks → Start New Import** → pick the connection + lookback window +
   which entity types to pull
2. Click **Start Import** → the pull runs (synchronous for MVP; can take a minute on a
   real company)
3. The import lands in `review` state with one row per QBO entity
4. Review the mappings — the rule-layer dictionary auto-classifies common patterns;
   ambiguous items are flagged for hand-review
5. **Commit** to materialize, **Rollback** if something looks wrong

### B7. Token refresh

Intuit access tokens expire after 1 hour. Refresh tokens are good for ~100 days. Click
**Refresh Token** on the connection to mint a new access token without re-doing OAuth.
For unattended sync, schedule `action_refresh_token` as a daily `ir.cron`.

## Known limitations (v1)

- The import is synchronous; large QBO companies (10K+ transactions) will hit Odoo's
  request timeout. Async via `queue_job` is a v2 follow-up.
- Transactions are NOT yet imported as journal entries — only the master data (accounts,
  partners, products) commits. Transaction import is a v2 follow-up.
- Export from Odoo back into QBO (IIF / CSV) is not yet implemented; the path is one-way
  (QBO → Odoo) for now.
- The `farm_csa_contract_glue` module is held back because OCA contract has no 19.0
  wheel yet — recurring CSA billing via OCA contracts will light up once that publishes.
