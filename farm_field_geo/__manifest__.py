{
    "name": "Farm Field — Geospatial",
    "version": "19.0.1.0.0",
    "summary": "PostGIS polygons + auto-computed acreage for farm.field",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    # Alpha matches farm_field; OCA's check-dev-status job rejects higher
    # dev-status modules depending on lower-status ones.
    "development_status": "Alpha",
    "depends": [
        "farm_field",
        "base_geoengine",
    ],
    "external_dependencies": {
        # pyproj: reproject WGS84 polygon → EPSG:5070 Albers for acreage.
        # shapely: base_geoengine already requires it; listed here to make
        # the dep graph explicit (CI's oca_install_addons uses this list).
        "python": ["pyproj", "shapely"],
    },
    "data": [
        "views/farm_field_views.xml",
    ],
    "installable": True,
    "application": False,
}
