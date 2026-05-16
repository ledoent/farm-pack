From a fresh Odoo 19 instance with this repo + its OCA dependencies on the
addons path:

```
odoo --init=farm_pack --stop-after-init -d <your_db>
```

For a populated demo (the storefront pre-configured with branded products,
30 partners, 6 weeks of orders, 4 CSA contracts, 3 delivery routes):

```
odoo --init=farm_pack,farm_pack_demo --stop-after-init -d <your_db>
```

(The `farm_pack_demo` module ships in a follow-up release.)
