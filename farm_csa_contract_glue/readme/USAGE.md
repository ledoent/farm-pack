1. Configure your CSA tiers (Farm → Configuration → CSA Tiers) with a
   product, cadence (weekly/biweekly/monthly), and `price_per_period`.
2. When a member signs up, create a `farm.csa.subscription` pointing at
   their tier.
3. Click **Activate** — the glue auto-creates a contract.contract under
   the hood. The button changes to **Open Contract**.
4. OCA contract's nightly `_recurring_create_invoice` cron will start
   issuing invoices on schedule. Set up payment provider integration
   (Stripe + Mandate) for fully-automatic recurring billing.
5. Cancel the subscription → contract lines get `date_end` = today, no
   further invoices issue.
