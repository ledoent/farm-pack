{
    "name": "Farm Observation",
    "version": "19.0.1.0.0",
    "summary": "Geotagged field observations (photos + notes, urgency-sorted)",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/ledoent/farm-pack",
    "license": "AGPL-3",
    "category": "Vertical/Agriculture",
    # Alpha matches farm_field_geo's chain — OCA check-dev-status gate.
    "development_status": "Alpha",
    "depends": [
        "farm_field_geo",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/farm_observation_views.xml",
        "views/farm_observation_menu.xml",
    ],
    "installable": True,
    "application": False,
}
