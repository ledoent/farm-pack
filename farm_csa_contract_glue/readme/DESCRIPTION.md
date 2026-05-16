Bridge `farm.csa.subscription` to OCA `contract.contract` so each CSA
member subscription becomes a real recurring-invoicing engine — no more
custom recurring logic.

When the CSA subscription is activated, the glue creates a contract with
one line per share product. The line's `recurring_rule_type` and
`recurring_interval` map from the tier's cadence:

| `farm.csa.tier.cadence` | OCA contract recurring |
|---|---|
| weekly | rule=weekly, interval=1 |
| biweekly | rule=weekly, interval=2 |
| monthly | rule=monthly, interval=1 |

From there, OCA's nightly cron generates recurring invoices on the
contract's schedule. The CSA subscription form gets two new buttons:

- **Create Contract** — manual trigger if you want to spin up a contract
  without activating the subscription
- **Open Contract** — jump to the linked contract record

Auto-create runs on `action_activate()`; manual create runs from the
button. Cancellation of the subscription sets `date_end` on all contract
lines (OCA contract doesn't have a single "terminate" action that fits
without a reason+date wizard).

**First module in the pack with an OCA-namespace dependency** —
specifically `OCA/contract`. Installs via pip from the OCA wheelhouse
(`odoo-addon-contract`).
