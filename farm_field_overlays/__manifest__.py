{
    "name": "Farm Field — Public Overlays",
    "version": "19.0.1.0.0",
    "summary": "USDA Cropland + NRCS Soil overlays on the field map",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    # Alpha matches farm_field_geo (and transitively farm_field); OCA's
    # check-dev-status gate rejects higher → lower dev-status deps.
    "development_status": "Alpha",
    "depends": [
        "farm_field_geo",
    ],
    "data": [
        "data/geoengine_raster_layers.xml",
    ],
    "installable": True,
    "application": False,
}
