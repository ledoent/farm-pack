from odoo.tests.common import TransactionCase


class TestFarmRankMixin(TransactionCase):
    """Smoke-test the mixin registers correctly and contributes the
    expected `rank` field. End-to-end sort behavior is covered by the
    consumer modules (farm_observation, farm_fence) which assert that
    records ordered by `rank desc` come out in priority order.

    We can't instantiate the AbstractModel directly with sample data —
    Odoo abstract models aren't backed by a table — so this test focuses
    on the field/attribute wiring contract subclasses rely on.
    """

    def test_abstract_model_is_registered(self):
        # Confirms farm_base/__init__.py imports the file so the registry
        # picks up the AbstractModel. If this assertion ever fails the
        # consumers will silently lose their `rank` column on next load.
        self.assertIn("farm.rank.mixin", self.env.registry)

    def test_rank_field_declared_with_required_attrs(self):
        # Subclasses inherit the field declaration; if it loses `store`
        # or `index` the priority sort silently becomes a Python sort
        # which won't hit Postgres indexes on large lists.
        mixin = self.env["farm.rank.mixin"]
        field = mixin._fields["rank"]
        self.assertEqual(field.type, "integer")
        self.assertTrue(field.store, "rank must be stored for SQL _order")
        self.assertTrue(field.index, "rank must be indexed for fast sort")
        self.assertTrue(field.readonly)

    def test_default_class_attrs_safe_when_unconfigured(self):
        # A subclass that forgets to set _rank_selection_field /
        # _rank_value_map should still load — the mixin's compute
        # falls back to rank=0 rather than raising. End-to-end wiring
        # for actual consumers (urgency, condition) is covered by the
        # regression tests in farm_observation + farm_fence.
        mixin = self.env["farm.rank.mixin"]
        self.assertEqual(mixin._rank_selection_field, "")
        self.assertEqual(mixin._rank_value_map, {})
