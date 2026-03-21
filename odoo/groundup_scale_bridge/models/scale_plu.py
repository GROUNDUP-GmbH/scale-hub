from odoo import api, fields, models


class GroundupScalePlu(models.Model):
    _name = "groundup.scale.plu"
    _description = "GroundUp Scale PLU Mapping"
    _order = "plu_number"
    _rec_name = "display_name"

    device_id = fields.Many2one(
        "groundup.scale.device",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        ondelete="restrict",
        index=True,
    )
    plu_number = fields.Integer(required=True, help="PLU number on the CAS scale (1–99999)")
    gtin = fields.Char(size=14, help="GTIN-13 or GTIN-14 for GS1 Digital Link")
    unit_price = fields.Float(
        digits=(10, 2),
        help="Price per kg/unit as configured on the scale",
    )
    last_synced = fields.Datetime(help="Last time this PLU was pushed to the scale")
    sync_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("synced", "Synced"),
            ("error", "Error"),
        ],
        default="pending",
    )

    display_name = fields.Char(compute="_compute_display_name", store=True)

    # LMIV Labeling Fields
    origin = fields.Char(help="Country/region of origin (LMIV Art. 9i)")
    ingredients = fields.Text(help="Ingredients list for processed products (LMIV Art. 9b)")
    allergens = fields.Char(help="Comma-separated allergen list (LMIV Art. 9c, Annex II)")
    shelf_life_days = fields.Integer(
        default=0,
        help="Days from packaging to best-before date. 0 = no MHD required.",
    )
    storage_instructions = fields.Char(help="Storage instructions (LMIV Art. 9g)")
    label_scenario = fields.Selection(
        [
            ("loose", "Lose / Loose"),
            ("simple_prepack", "Einfach vorverpackt / Simple Prepack"),
            ("full_prepack", "Voll vorverpackt / Full Prepack"),
            ("leh_prepack", "LEH / Retail Prepack"),
        ],
        default="simple_prepack",
        help="Label scenario determines which fields are mandatory (LMIV).",
    )
    marketing_class = fields.Selection(
        [
            ("extra", "Extra"),
            ("I", "Klasse I"),
            ("II", "Klasse II"),
        ],
        help="EU marketing standard class for fresh produce.",
    )
    # Nutrition (Big Seven, LMIV Art. 30) — per 100g/100ml
    energy_kj = fields.Float(digits=(10, 1), help="Energy in kJ per 100g")
    energy_kcal = fields.Float(digits=(10, 1), help="Energy in kcal per 100g")
    fat = fields.Float(digits=(10, 1), help="Fat in g per 100g")
    saturated_fat = fields.Float(digits=(10, 1), help="Saturated fat in g per 100g")
    carbohydrates = fields.Float(digits=(10, 1), help="Carbohydrates in g per 100g")
    sugars = fields.Float(digits=(10, 1), help="Sugars in g per 100g")
    protein = fields.Float(digits=(10, 1), help="Protein in g per 100g")
    salt = fields.Float(digits=(10, 2), help="Salt in g per 100g")

    _sql_constraints = [
        (
            "device_plu_unique",
            "UNIQUE(device_id, plu_number)",
            "PLU number must be unique per device.",
        ),
    ]

    @api.depends("plu_number", "product_id")
    def _compute_display_name(self):
        for rec in self:
            product = rec.product_id.name if rec.product_id else "?"
            rec.display_name = f"PLU {rec.plu_number}: {product}"
