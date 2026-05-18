"""Thin wrapper around the Intuit QuickBooks Online API.

Falls back to a deterministic stub when the intuit-oauth / python-quickbooks
libraries are not installed (CI base image, design-partner sandboxes without
Intuit credentials). The stub returns a small fixture matching the real API
shape so downstream code is testable without real Intuit access.
"""

import logging

_logger = logging.getLogger(__name__)

try:
    from intuitlib.client import AuthClient
    from quickbooks import QuickBooks

    HAS_INTUIT_LIBS = True
except ImportError:  # pragma: no cover - optional path for stubbed env
    AuthClient = None
    QuickBooks = None
    HAS_INTUIT_LIBS = False


class IntuitClient:
    """Wraps Intuit OAuth + API calls. Stubbed when libs unavailable."""

    def __init__(self, connection):
        self.connection = connection
        self._client = None

    def is_live(self):
        return HAS_INTUIT_LIBS and bool(
            self.connection.access_token and self.connection.realm_id
        )

    def refresh_access_token(self):
        """Exchange the stored refresh token for a fresh access token.

        Returns a dict matching Intuit's token response shape:
        ``{access_token, refresh_token, expires_in, x_refresh_token_expires_in}``.
        Caller writes the values back onto the farm.qbo.connection record.
        """
        if not HAS_INTUIT_LIBS:
            raise RuntimeError(
                "intuit-oauth not installed; cannot refresh access token."
            )
        auth = AuthClient(
            client_id="STUB",  # configured via ir.config_parameter in v1
            client_secret="STUB",
            environment=self.connection.environment,
            redirect_uri="https://localhost/farm_qbo/oauth/callback",
        )
        auth.refresh_token = self.connection.refresh_token
        auth.refresh()
        return {
            "access_token": auth.access_token,
            "refresh_token": auth.refresh_token,
            "expires_in": auth.expires_in,
        }

    def _real_client(self):
        if not HAS_INTUIT_LIBS:
            raise RuntimeError(
                "intuit-oauth / python-quickbooks not installed; "
                "running in stub mode only."
            )
        if self._client is None:
            auth = AuthClient(
                client_id="STUB",  # configured via ir.config_parameter in v1
                client_secret="STUB",
                environment=self.connection.environment,
                redirect_uri="https://localhost/farm_qbo/oauth/callback",
            )
            auth.access_token = self.connection.access_token
            auth.refresh_token = self.connection.refresh_token
            self._client = QuickBooks(
                auth_client=auth,
                refresh_token=self.connection.refresh_token,
                company_id=self.connection.realm_id,
            )
        return self._client

    def pull_accounts(self):
        if not self.is_live():
            return _stub_accounts()
        from quickbooks.objects.account import Account  # noqa: PLC0415

        return [a.to_dict() for a in Account.all(qb=self._real_client())]

    def pull_vendors(self):
        if not self.is_live():
            return _stub_vendors()
        from quickbooks.objects.vendor import Vendor  # noqa: PLC0415

        return [v.to_dict() for v in Vendor.all(qb=self._real_client())]

    def pull_customers(self):
        if not self.is_live():
            return _stub_customers()
        from quickbooks.objects.customer import Customer  # noqa: PLC0415

        return [c.to_dict() for c in Customer.all(qb=self._real_client())]

    def pull_items(self):
        if not self.is_live():
            return _stub_items()
        from quickbooks.objects.item import Item  # noqa: PLC0415

        return [i.to_dict() for i in Item.all(qb=self._real_client())]


def _stub_accounts():
    return [
        {
            "Id": "1",
            "Name": "Sales of Eggs",
            "AcctNum": "4100",
            "Classification": "Revenue",
            "AccountType": "Income",
            "AccountSubType": "SalesOfProductIncome",
        },
        {
            "Id": "2",
            "Name": "Sales of Produce",
            "AcctNum": "4200",
            "Classification": "Revenue",
            "AccountType": "Income",
            "AccountSubType": "SalesOfProductIncome",
        },
        {
            "Id": "3",
            "Name": "Feed Purchased",
            "AcctNum": "5100",
            "Classification": "Expense",
            "AccountType": "Cost of Goods Sold",
            "AccountSubType": "SuppliesMaterialsCogs",
        },
        {
            "Id": "4",
            "Name": "Fuel - Vehicles",
            "AcctNum": "5200",
            "Classification": "Expense",
            "AccountType": "Expense",
            "AccountSubType": "Auto",
        },
        {
            "Id": "5",
            "Name": "Operating Bank",
            "AcctNum": "1100",
            "Classification": "Asset",
            "AccountType": "Bank",
            "AccountSubType": "Checking",
        },
    ]


def _stub_vendors():
    return [
        {
            "Id": "v1",
            "DisplayName": "Local Feed Co-Op",
            "PrimaryEmailAddr": {"Address": "orders@feedcoop.example"},
        },
        {
            "Id": "v2",
            "DisplayName": "Tractor Supply",
            "PrimaryEmailAddr": {"Address": "billing@tractor.example"},
        },
    ]


def _stub_customers():
    return [
        {
            "Id": "c1",
            "DisplayName": "Alice Neighbour",
            "PrimaryEmailAddr": {"Address": "alice@example.com"},
        },
        {
            "Id": "c2",
            "DisplayName": "Boyd's Wellness Pantry",
            "PrimaryEmailAddr": {"Address": "buyer@boyds.example"},
        },
    ]


def _stub_items():
    return [
        {"Id": "i1", "Name": "Dozen Eggs - Pastel Mix", "UnitPrice": 6.0},
        {"Id": "i2", "Name": "Salad Greens (bag)", "UnitPrice": 4.5},
        {"Id": "i3", "Name": "CSA Family Weekly", "UnitPrice": 42.0},
    ]
