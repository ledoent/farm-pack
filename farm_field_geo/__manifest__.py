{
    "name": "Farm Field — Geospatial",
    "version": "19.0.1.0.0",
    "summary": "PostGIS polygons + auto-computed acreage for farm.field",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_field",
        "base_geoengine",
    ],
    "data": [
        "views/farm_field_views.xml",
    ],
    "installable": True,
    "application": False,
}
