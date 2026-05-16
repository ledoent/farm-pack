from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    farm_qbo_client_id = fields.Char(
        string="Intuit App Client ID",
        config_parameter="farm_qbo.client_id",
        help="From the Keys tab of your Intuit Developer app. Separate values "
        "for Development and Production — pick the one matching your "
        "connection's environment.",
    )
    farm_qbo_client_secret = fields.Char(
        string="Intuit App Client Secret",
        config_parameter="farm_qbo.client_secret",
    )
    farm_qbo_redirect_uri = fields.Char(
        string="OAuth Redirect URI",
        config_parameter="farm_qbo.redirect_uri",
        help="Must match exactly what you configured in the Intuit app's "
        "Redirect URIs list. Typically https://your-host/farm_qbo/oauth/callback.",
    )
