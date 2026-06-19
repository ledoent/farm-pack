{
    "name": "Farm Onboarding",
    "summary": "60-second first-run wizard for new farm-pack installs",
    "version": "19.0.1.1.0",
    "license": "AGPL-3",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/ledoent/farm-pack",
    "category": "Vertical/Agriculture",
    "depends": [
        "farm_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/farm_enterprise_type_data.xml",
        "views/farm_onboarding_session_views.xml",
        "views/farm_enterprise_type_views.xml",
        "views/farm_onboarding_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "farm_onboarding/static/src/js/onboarding_systray.esm.js",
            "farm_onboarding/static/src/xml/onboarding_systray.xml",
        ],
    },
    "demo": [],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
    "maintainers": ["dkendall"],
}
