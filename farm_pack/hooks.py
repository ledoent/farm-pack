import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Seed onboarding sessions for existing farm users.

    Without this, an install against a live db leaves every existing
    user with a hidden menu item and no nudge — the systray bell only
    pulses when there's an active session. New users created after
    install pick up a session lazily via
    `farm.onboarding.session.get_or_create_for_current_user`.

    Scope: internal users (share=False) who belong to the farm-user
    group. Portal users, the public user, and SaaS-tenant tooling
    accounts are intentionally excluded.
    """
    Session = env["farm.onboarding.session"]
    farm_user_group = env.ref("farm_base.group_farm_user")
    farm_users = env["res.users"].search(
        [
            ("share", "=", False),
            ("active", "=", True),
            ("groups_id", "in", farm_user_group.id),
        ]
    )
    seeded = 0
    for user in farm_users:
        for company in user.company_ids:
            existing = Session.search_count(
                [
                    ("user_id", "=", user.id),
                    ("company_id", "=", company.id),
                ]
            )
            if existing:
                continue
            Session.create(
                {
                    "user_id": user.id,
                    "company_id": company.id,
                    "farm_name": company.name,
                }
            )
            seeded += 1
    if seeded:
        _logger.info("farm_pack post_init_hook seeded %d onboarding session(s)", seeded)
    else:
        # Idempotent re-run / fresh db with no farm users — quiet path.
        _logger.debug("farm_pack post_init_hook: no new onboarding sessions to seed")
