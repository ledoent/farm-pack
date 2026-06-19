Adds a navbar systray bell (leaf icon + red badge dot) that surfaces
the setup wizard whenever the current farm user has an unfinished
onboarding session. The bell is hidden for users outside the
`farm_base.group_farm_user` group and disappears once the session
is marked done.

New `farm.onboarding.session.count_pending_for_current_user` RPC
endpoint drives the bell's visibility — read-only, scoped to the
current `(user, company)`, kept separate from
`get_or_create_for_current_user` so page loads cannot create rows.
