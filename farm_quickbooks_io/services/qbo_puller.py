"""Service: pull QBO entities according to an import session's options."""

import logging

from .intuit_client import IntuitClient

_logger = logging.getLogger(__name__)


class QboPuller:
    def __init__(self, import_session):
        self.session = import_session
        self.client = IntuitClient(import_session.connection_id)

    def pull(self):
        accounts, partners, products = [], [], []
        if self.session.include_coa:
            accounts = self.client.pull_accounts()
        if self.session.include_partners:
            partners = self.client.pull_vendors() + self.client.pull_customers()
        if self.session.include_products:
            products = self.client.pull_items()
        return {
            "accounts": accounts,
            "partners": partners,
            "products": products,
            "summary": {
                "live": self.client.is_live(),
                "account_count": len(accounts),
                "partner_count": len(partners),
                "product_count": len(products),
            },
        }
