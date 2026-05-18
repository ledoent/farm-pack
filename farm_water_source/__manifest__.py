{
    "name": "Farm Water Source",
    "version": "19.0.1.0.0",
    "summary": "Wells, ponds, troughs, springs — geometry + which fields they serve",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    # Alpha matches farm_field_geo's chain — OCA check-dev-status gate.
    "development_status": "Alpha",
    "depends": [
        "farm_field_geo",
    ],
    "external_dependencies": {
        "python": ["shapely"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/farm_water_source_views.xml",
        "views/farm_water_source_menu.xml",
    ],
    "installable": True,
    "application": False,
}
