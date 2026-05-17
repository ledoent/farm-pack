from odoo.tests.common import TransactionCase


class TestFarmFieldOverlays(TransactionCase):
    """Smoke-check the three overlay records ship correctly bound to the
    farm.field geoengine view. Catches XML-ref breakage if either the
    raster layer model or the view xmlid moves under us.
    """

    def test_overlays_are_bound_to_field_geoengine_view(self):
        view = self.env.ref("farm_field_geo.farm_field_view_geoengine")
        for xmlid in (
            "farm_field_overlays.farm_field_overlay_cdl",
            "farm_field_overlays.farm_field_overlay_ssurgo",
            "farm_field_overlays.farm_field_overlay_osm",
        ):
            layer = self.env.ref(xmlid)
            self.assertEqual(
                layer.view_id, view, f"{xmlid} should be bound to the field map"
            )

    def test_wms_overlays_carry_layer_param(self):
        # Both WMS records must specify a LAYERS param — without it the WMS
        # GetMap request returns a 400 and the overlay silently fails.
        for xmlid in (
            "farm_field_overlays.farm_field_overlay_cdl",
            "farm_field_overlays.farm_field_overlay_ssurgo",
        ):
            layer = self.env.ref(xmlid)
            self.assertEqual(layer.raster_type, "d_wms")
            self.assertIn("LAYERS", layer.params_wms or "")

    def test_osm_basemap_is_not_an_overlay(self):
        # OSM sits underneath as a basemap; overlay=False keeps it from
        # blanking out the WMS layers above it.
        osm = self.env.ref("farm_field_overlays.farm_field_overlay_osm")
        self.assertEqual(osm.raster_type, "osm")
        self.assertFalse(osm.overlay)
