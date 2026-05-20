Adds a `post_init_hook` that seeds one `farm.onboarding.session` per
(internal farm user, company) pair on install. Existing installs
upgrade and surface the `farm_onboarding` navbar bell immediately
instead of waiting for users to discover the **Farm → Setup Wizard**
menu item.

Portal users (`share=True`) and tooling accounts are excluded. The
hook is idempotent — re-running it after an upgrade does not
duplicate sessions.
