"""Intuit OAuth flow controllers.

MVP: the /authorize endpoint returns instructions (no live OAuth dance yet —
client_id/client_secret are not configured). v1: wires real intuit-oauth
authorization URL and callback token exchange.
"""

from odoo import http
from odoo.http import request


class FarmQboOauthController(http.Controller):
    @http.route(
        "/farm_qbo/oauth/authorize",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def authorize(self, connection_id=None, **kw):
        env = request.env
        if not connection_id:
            return request.make_response("Missing connection_id parameter.", status=400)
        connection = env["farm.qbo.connection"].browse(int(connection_id))
        if not connection.exists():
            return request.make_response("Unknown connection.", status=404)
        return request.make_response(
            (
                "<h2>QuickBooks OAuth (MVP stub)</h2>"
                f"<p>Connection {connection.id} - environment "
                f"{connection.environment}.</p>"
                "<p>Live Intuit OAuth flow ships in v1. For now, paste tokens "
                "manually into the connection form.</p>"
            ),
            headers=[("Content-Type", "text/html; charset=utf-8")],
        )

    @http.route(
        "/farm_qbo/oauth/callback",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def callback(self, **kw):
        return request.make_response(
            (
                "<h2>QuickBooks callback (MVP stub)</h2>"
                "<p>Token exchange ships in v1.</p>"
            ),
            headers=[("Content-Type", "text/html; charset=utf-8")],
        )
