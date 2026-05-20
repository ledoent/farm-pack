Single-install entry point for the ledoent farm pack. Composes the four
jobs the farm app must do well — website, online ordering, weekly delivery
routes, and QuickBooks compatibility — by pulling in the Odoo CE storefront +
sales + delivery + accounting stack alongside ledoent's thin farm-specific
glue.

Customers install `farm_pack` and get the full stack. Power users can also
install the leaf modules individually (`farm_egg_production`, `farm_csa`,
`farm_delivery_routes`) for narrower deployments.

Composition rationale and the four-jobs plan: see
[plans/2-farm-pack-composition.md](https://github.com/ledoent/farm-pack/blob/main/plans/2-farm-pack-composition.md).

On install, a `post_init_hook` seeds one `farm.onboarding.session` per
(internal farm user, company) pair so the navbar bell from
`farm_onboarding` shows up immediately for every existing farm user.
Portal users and tooling accounts are excluded. The hook is idempotent
— re-running it (e.g., after an upgrade) does not duplicate sessions.
