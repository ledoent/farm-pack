First-run setup wizard for the farm pack. Five screens — welcome, your
farm (name + acres + ZIP), what you grow or raise (multi-select from 12
enterprise types), how you keep books today (QBO / QBD / Excel / paper /
nothing), done — with a state machine, progress bar, save-as-you-go, and
back/next/skip/restart actions.

This MVP uses a regular form view with state-conditional groups so
sessions persist across browser closes. The original plan called for an
OWL client action with full-screen modal; that polish is deferred to
v1 in favor of shipping the data model and flow first.

Adds 12 pre-loaded `farm.enterprise.type` records (eggs, vegetables,
fruit, herbs, orchard, cattle, dairy, poultry, hogs, sheep/goats, value-
added, workshops) with emoji icons — these drive product catalog and
report pre-configuration in downstream modules.

The "Setup Wizard" menu item routes each user to their own open session
(creates one if none exists), so multiple farm-users on the same company
each get an independent walkthrough.
