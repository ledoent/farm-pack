First-run setup wizard for the farm pack. Five screens — welcome, your
farm (name + acres + ZIP), what you grow or raise (multi-select from 12
enterprise types), how you keep books today (QBO / QBD / Excel / paper /
nothing), done — with a state machine, progress bar, save-as-you-go, and
back/next/skip/restart actions.

The wizard surfaces itself two ways:

- **Navbar bell.** A leaf icon with a red badge dot appears in the
  systray when the current farm user has an unfinished session. Click
  it to jump straight into the wizard. The bell is hidden for users
  outside `farm_base.group_farm_user` and disappears once the session
  is marked done.
- **Farm → Setup Wizard menu item.** Same destination, accessible at
  any time for a re-run.

The form itself is a regular Odoo form view with state-conditional
groups so sessions persist across browser closes. A richer custom-
chrome design pass lives in a follow-on PR (Step 2 of the UX
refinement plan).

Adds 12 pre-loaded `farm.enterprise.type` records (eggs, vegetables,
fruit, herbs, orchard, cattle, dairy, poultry, hogs, sheep/goats, value-
added, workshops) with emoji icons — these drive product catalog and
report pre-configuration in downstream modules.

Each user gets their own session per company, so multiple farm-users on
the same company each get an independent walkthrough. The umbrella
`farm_pack` module's `post_init_hook` seeds a session for every existing
internal farm user on install; new users created later pick one up
lazily on first wizard open.
