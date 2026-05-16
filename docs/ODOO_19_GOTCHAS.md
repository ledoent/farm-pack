# Odoo 19 gotchas — catalog of CI failures we've hit and their fixes

Bookmark this. Every entry below cost a CI round-trip. Each new module risks discovering
more.

## Model definition

### `_sql_constraints` no longer supported

**Before (17/18):**

```python
_sql_constraints = [
    ("name_unique", "UNIQUE (name)", "Name must be unique."),
]
```

**After (19+):**

```python
_name_unique = models.Constraint(
    "UNIQUE (name)",
    "Name must be unique.",
)
```

Declared as class-level attributes. The constraint name becomes the attribute name
(`_name_unique` here).

### `group_operator=` field arg removed

**Before:**

```python
total = fields.Float(group_operator="sum")
```

**After:**

```python
total = fields.Float(aggregator="sum")
```

CI's checklog promotes the DeprecationWarning to a failure.

### Field label collisions on the same model

If your inherit adds a field whose `string="..."` matches an existing field's label on
the SAME model, Odoo logs WARNING and checklog fails.

**Symptom:**

> Two fields (farm_delivery_date, commitment_date) of sale.order have the same label:
> Delivery Date.

**Fix:** Use a distinct `string=` ("Route Delivery Date") or drop the `string=` entirely
(the field name auto-capitalizes).

### Redundant `string=` is a pylint-odoo warning

If `string="Farm Name"` exactly matches the auto-generated label from a field named
`farm_name`, pylint-odoo flags it as `W8113 attribute-string-redundant`. Drop the
`string=`.

## Security model

### `res.groups.category_id` removed

**Before:**

```xml
<record id="my_group" model="res.groups">
  <field name="category_id" ref="my_module_category" />
</record>
```

**After (19+):**

```xml
<!-- First create a Privilege grouping the related groups -->
<record id="my_privilege" model="res.groups.privilege">
    <field name="name">My Module</field>
    <field name="category_id" ref="my_module_category"/>
    <field name="sequence">10</field>
</record>
<!-- Then groups point at the privilege, not directly at the category -->
<record id="group_my_user" model="res.groups">
    <field name="privilege_id" ref="my_privilege"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### `res.groups.users` renamed to `user_ids`

**Before:** `<field name="users" eval="[(4, ref('base.user_admin'))]"/>` **After:**
`<field name="user_ids" eval="[(4, ref('base.user_admin'))]"/>`

## Views

### Search view `<group string="Group By">` is rejected

In Odoo 19 the RelaxNG schema rejects `string=` on `<group>` inside `<search>`. Just use
`<group>` bare — the "Group By" label is auto-rendered for any filters with
`context="{'group_by': X}"`.

**Before:**

```xml
<group string="Group By">
  <filter name="grp_state" context="{'group_by': 'state'}" string="State" />
</group>
```

**After:**

```xml
<group>
  <filter name="grp_state" context="{'group_by': 'state'}" string="State" />
</group>
```

### `<separator/>` between `<field>` and `<filter>` is rejected

In a search view, `<separator/>` is only valid between filter groups, not between field
elements and filter elements. Drop it or move it.

### Self-closing XML tags need a space before `/>`

prettier-with-plugin-xml insists: `<field />` not `<field/>`. Auto-fixed by the prettier
hook.

### Web routes should `raise` HTTPException, not `return`

```python
# Wrong — checklog catches this as a WARNING and fails the build
if not record:
    return request.not_found()

# Right
if not record:
    raise request.not_found()
```

Also: tests that intentionally hit a `not_found` route need `mute_logger("odoo.http")`
around the request to keep the WARNING out of the test log.

## Units of measure

### `uom.category` model removed entirely

Odoo 19 rearchitected UoMs. The old `uom.category` +
`factor`/`factor_inv`/`uom_type`/`rounding` is gone. New model:

```python
# 17/18
uom_id = fields.Many2one("uom.uom")
# referenced records like:
<record id="my_unit" model="uom.uom">
    <field name="category_id" ref="uom.uom_categ_kgm"/>
    <field name="uom_type">bigger</field>
    <field name="factor_inv">2.20</field>
    <field name="rounding">0.01</field>
</record>
```

**After:** UoMs chain via `relative_uom_id` + `relative_factor`. The `rounding` is
computed from `decimal.precision('Product Unit')`, not stored per-UoM. `uom_type` is
gone — derived from whether `relative_uom_id` is null.

```xml
<record id="my_unit" model="uom.uom">
    <field name="name">Kilogram</field>
    <field name="relative_factor" eval="1.0"/>
</record>
<record id="my_pack_unit" model="uom.uom">
    <field name="name">Pack of 6</field>
    <field name="relative_factor" eval="6"/>
    <field name="relative_uom_id" ref="my_unit"/>
</record>
```

## CE module renames

### `website_sale_delivery` folded into `website_sale`

In Odoo 17 the delivery-method selection at checkout moved into `website_sale` itself.
**Don't add `website_sale_delivery` to `depends`** — pip will report "No matching
distribution found for odoo-addon-website_sale_delivery==19.0.\*".

## OCA wheelhouse caveats

The wheelhouse at `https://wheelhouse.odoo-community.org/oca-simple-and-pypi` lags
behind OCA repo branches. **The repo having a 19.0 branch is not the same as the wheel
being published.** Always verify:

```bash
pip install --index-url=https://wheelhouse.odoo-community.org/oca-simple-and-pypi \
  --dry-run "odoo-addon-<MODULE>==19.0.*"
```

We've hit this with `odoo-addon-contract` — repo branch exists, wheel doesn't. Held
`farm_csa_contract_glue` as `installable: False` until OCA publishes.

## OCA workflow conventions

### `makepot` step needs a `GIT_PUSH_TOKEN` secret

The OCA copier template's test workflow has a `Update .pot files` step that pushes
generated translations back to the repo via a `GIT_PUSH_TOKEN` repo secret. Without that
secret, the step fails on `git push` with "Password authentication is not supported."

Either create the secret OR remove `makepot: "true"` from the OCB matrix entry in
`.github/workflows/test.yml` (the latter is what we did since we don't ship translations
yet).

### OCA `position="replace"` warning

`xml-dangerous-qweb-replace-low-priority` fires when a template inherits with
`position="replace"` at default priority. Use `t-call="website.layout"` inside a primary
template instead of inheriting + replacing.

## Translation API

### `_()` → `self.env._()` with kwargs

Odoo PR 174844 moved translation off the module-level `_()`. Use `self.env._(...)` and
named placeholders:

```python
# Before
raise UserError(_("Bad %s and %s") % (a, b))

# After
raise UserError(self.env._("Bad %(a)s and %(b)s", a=a, b=b))
```

pylint-odoo flags positional `%s` in translations as
`W8120 translation-positional-used`.

## Test patterns

### Specific exception, not bare `Exception`

ruff B017 forbids `assertRaises(Exception)`. Use specific exceptions (`ValidationError`,
`UserError`, `psycopg2.errors.UniqueViolation`, etc.).

### `mute_logger` around expected errors

When a test intentionally triggers something that logs an ERROR or WARNING (constraint
violation, 404 route), wrap in `mute_logger` to keep checklog quiet:

```python
from odoo.tools.misc import mute_logger

with mute_logger("odoo.sql_db"), self.assertRaises(UniqueViolation):
    with self.env.cr.savepoint():
        Model.create({"name": "duplicate"})
```

## Closure capture in lambdas

ruff B023 catches `lambda x: x.field == rec.attr` inside a `for rec in self:` loop — the
lambda captures `rec` by reference and all iterations see the final value. Bind
explicitly:

```python
# Wrong
for rec in self:
    found = others.filtered(lambda o: o.x == rec.x)

# Right
for rec in self:
    target = rec.x
    found = others.filtered(lambda o, t=target: o.x == t)
```
