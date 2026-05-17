from odoo.tests.common import TransactionCase


class TestFarmCrop(TransactionCase):
    def test_seeded_catalog_loaded(self):
        """Seed catalog from data/farm_crop_data.xml should land at install."""
        tomato = self.env.ref("farm_crop.crop_tomato")
        self.assertEqual(tomato.name, "Tomato")
        self.assertEqual(tomato.category, "vegetable")
        self.assertEqual(tomato.family, "Solanaceae")

    def test_create_custom_crop(self):
        """Farmers can add their own crops."""
        crop = self.env["farm.crop"].create(
            {"name": "Heirloom Cherokee Purple", "category": "vegetable"}
        )
        self.assertEqual(crop.name, "Heirloom Cherokee Purple")
        self.assertTrue(crop.active)

    def test_image_thumbnail_stored(self):
        """image_128 should be computed/stored from image_1920."""
        # 1×1 transparent PNG, base64
        png = (
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAA"
            b"AAYAAjCB0C8AAAAASUVORK5CYII="
        )
        crop = self.env["farm.crop"].create({"name": "Picture Crop", "image_1920": png})
        self.assertTrue(crop.image_128)
