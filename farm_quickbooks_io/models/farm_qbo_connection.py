from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class FarmQboConnection(models.Model):
    _name = "farm.qbo.connection"
    _description = "QuickBooks Online Connection"
    _inherit = ["mail.thread"]
    _order = "company_id, id"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    environment = fields.Selection(
        [
            ("sandbox", "Sandbox"),
            ("production", "Production"),
        ],
        default="sandbox",
        required=True,
        tracking=True,
    )
    realm_id = fields.Char(
        help="QuickBooks Online company ID (also called 'realm ID').",
        tracking=True,
    )
    access_token = fields.Char(
        help="Short-lived access token. Auto-refreshed via the refresh token. "
        "Plain-text in MVP; v1 reads from ir.config_parameter with vault.",
    )
    refresh_token = fields.Char(
        help="Long-lived refresh token used to mint new access tokens.",
    )
    token_expires_at = fields.Datetime()
    last_synced_at = fields.Datetime(readonly=True)
    state = fields.Selection(
        [
            ("disconnected", "Disconnected"),
            ("connected", "Connected"),
            ("expired", "Token Expired"),
            ("revoked", "Revoked"),
        ],
        compute="_compute_state",
        store=True,
    )
    import_ids = fields.One2many("farm.qbo.import", "connection_id")
    import_count = fields.Integer(compute="_compute_import_count")

    @api.depends("environment", "realm_id")
    def _compute_name(self):
        for rec in self:
            if rec.realm_id:
                rec.name = f"QBO {rec.environment} · {rec.realm_id}"
            else:
                rec.name = self.env._("QuickBooks Connection (unconfigured)")

    @api.depends("access_token", "refresh_token", "token_expires_at")
    def _compute_state(self):
        now = fields.Datetime.now()
        for rec in self:
            if not rec.refresh_token:
                rec.state = "disconnected"
            elif rec.token_expires_at and rec.token_expires_at < now:
                rec.state = "expired"
            elif rec.access_token:
                rec.state = "connected"
            else:
                rec.state = "disconnected"

    @api.depends("import_ids")
    def _compute_import_count(self):
        for rec in self:
            rec.import_count = len(rec.import_ids)

    def action_open_authorize_url(self):
        """Return a client action opening the Intuit OAuth authorize URL."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/farm_qbo/oauth/authorize?connection_id={self.id}",
            "target": "new",
        }

    def action_disconnect(self):
        self.write(
            {
                "access_token": False,
                "refresh_token": False,
                "token_expires_at": False,
                "realm_id": False,
            }
        )

    def action_refresh_token(self):
        """Mint a fresh access token using the stored refresh token.

        Called from the form-view header button when state ∈ {connected,
        expired}. Delegates the actual round-trip to the intuit-oauth
        library via `services.intuit_client.IntuitClient`; bails with a
        clear UserError if either the refresh token is missing or the
        intuit-oauth libs aren't installed (stub mode).
        """
        self.ensure_one()
        if not self.refresh_token:
            raise UserError(
                self.env._(
                    "No refresh token stored. Click Connect QuickBooks to "
                    "complete the OAuth flow first."
                )
            )
        # Lazy import keeps stub-mode installs (no intuit-oauth wheel) from
        # crashing at module-load time.
        from ..services.intuit_client import (  # noqa: PLC0415
            HAS_INTUIT_LIBS,
            IntuitClient,
        )

        if not HAS_INTUIT_LIBS:
            raise UserError(
                self.env._(
                    "intuit-oauth library is not installed. Install "
                    "`intuit-oauth` + `python-quickbooks` to refresh tokens."
                )
            )
        client = IntuitClient(self)
        new_tokens = client.refresh_access_token()
        self.write(
            {
                "access_token": new_tokens["access_token"],
                "refresh_token": new_tokens.get("refresh_token", self.refresh_token),
                "token_expires_at": fields.Datetime.now()
                + timedelta(seconds=new_tokens.get("expires_in", 3600)),
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": self.env._("Token refreshed"),
                "message": self.env._(
                    "New access token valid until %s.",
                    self.token_expires_at,
                ),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
