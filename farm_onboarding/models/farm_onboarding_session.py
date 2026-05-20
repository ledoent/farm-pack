from odoo import api, fields, models

STATE_ORDER = ["welcome", "farm_profile", "enterprises", "books", "done"]


class FarmOnboardingSession(models.Model):
    _name = "farm.onboarding.session"
    _description = "Farm Onboarding Session"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        required=True,
    )
    state = fields.Selection(
        [
            ("welcome", "Welcome"),
            ("farm_profile", "Your Farm"),
            ("enterprises", "What You Grow / Raise"),
            ("books", "Books Today"),
            ("done", "All Set"),
        ],
        default="welcome",
        required=True,
        tracking=True,
    )
    progress_pct = fields.Integer(
        compute="_compute_progress_pct",
        help="Percent through the onboarding sequence.",
    )

    # Screen 2 — your farm
    farm_name = fields.Char()
    acreage = fields.Float(string="Acres", digits=(8, 2))
    zip_code = fields.Char(string="ZIP")

    # Screen 3 — enterprises
    enterprise_ids = fields.Many2many(
        "farm.enterprise.type",
        string="What You Grow / Raise",
    )

    # Screen 4 — books
    bookkeeping_method = fields.Selection(
        [
            ("qbo", "QuickBooks Online"),
            ("qbd", "QuickBooks Desktop"),
            ("excel", "Excel / Google Sheets"),
            ("paper", "Paper / Notebook"),
            ("nothing", "Nothing yet"),
        ],
        string="How are you keeping books today?",
    )
    finished_at = fields.Datetime(readonly=True)

    @api.depends("company_id", "state")
    def _compute_name(self):
        for sess in self:
            label = dict(self._fields["state"].selection).get(sess.state, "")
            sess.name = (
                f"{sess.company_id.name} · {label}"
                if sess.company_id
                else self.env._("New Onboarding")
            )

    @api.depends("state")
    def _compute_progress_pct(self):
        for sess in self:
            try:
                idx = STATE_ORDER.index(sess.state)
            except ValueError:
                idx = 0
            sess.progress_pct = int(round((idx / (len(STATE_ORDER) - 1)) * 100))

    def _next_state(self, current):
        try:
            return STATE_ORDER[STATE_ORDER.index(current) + 1]
        except (ValueError, IndexError):
            return "done"

    def _prev_state(self, current):
        try:
            return STATE_ORDER[max(0, STATE_ORDER.index(current) - 1)]
        except ValueError:
            return "welcome"

    def action_next(self):
        for sess in self:
            sess.state = self._next_state(sess.state)
            if sess.state == "done":
                sess.finished_at = fields.Datetime.now()

    def action_back(self):
        for sess in self:
            sess.state = self._prev_state(sess.state)

    def action_skip(self):
        self.write({"state": "done", "finished_at": fields.Datetime.now()})

    def action_restart(self):
        self.write({"state": "welcome", "finished_at": False})

    @api.model
    def get_or_create_for_current_user(self):
        """Return the active session for current user's company, creating one
        if none exists. Used by the menu action to land on the right record."""
        session = self.search(
            [
                ("company_id", "=", self.env.company.id),
                ("user_id", "=", self.env.user.id),
                ("state", "!=", "done"),
            ],
            limit=1,
        )
        if not session:
            session = self.create(
                {
                    "company_id": self.env.company.id,
                    "user_id": self.env.user.id,
                    "farm_name": self.env.company.name,
                }
            )
        return session

    @api.model
    def count_pending_for_current_user(self):
        """Pending-session count for the systray bell.

        Kept separate from `get_or_create_for_current_user` so the
        bell's mount path is read-only — the systray must not create
        session rows on every page load.
        """
        return self.search_count(
            [
                ("company_id", "=", self.env.company.id),
                ("user_id", "=", self.env.user.id),
                ("state", "!=", "done"),
            ]
        )

    def action_open_for_current_user(self):
        session = self.get_or_create_for_current_user()
        return {
            "type": "ir.actions.act_window",
            "res_model": "farm.onboarding.session",
            "res_id": session.id,
            "view_mode": "form",
            "target": "current",
        }
