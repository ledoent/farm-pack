1. **Farm → QuickBooks → Connections**: create one record per QBO company,
   pick sandbox or production, paste your realm ID. In MVP, also paste the
   access + refresh tokens manually (Intuit OAuth Playground works); v1
   adds the in-app authorization flow.
2. **Farm → QuickBooks → Start New Import**: pick connection, lookback
   window, and what to pull (CoA / partners / products / transactions).
3. Hit **Start Import**: opens the import record in the **Mappings**
   notebook with one row per QBO entity — review the rule-layer proposals,
   override anything you don't like.
4. **Commit**: materialises accepted mappings as `account.account`,
   `res.partner`, and `product.product` records. Every record carries an
   audit reference back to its QBO source.
5. **Rollback** if a mapping was wrong: deletes the committed records
   (best-effort — fails closed on downstream FK constraints).

Without `intuit-oauth` / `python-quickbooks` installed the module runs in
**stub mode** with a deterministic fixture — useful for demos, training,
and CI.
