from odoo import api, fields, models


class GroundupScaleLog(models.Model):
    _name = "groundup.scale.log"
    _description = "GroundUp Scale Audit Log"
    _order = "create_date desc"
    _rec_name = "display_name"

    event_type = fields.Selection(
        [
            ("hub_started", "Hub Started"),
            ("hub_stopped", "Hub Stopped"),
            ("plu_selected", "PLU Selected"),
            ("plu_select_failed", "PLU Select Failed"),
            ("sale_completed", "Sale Completed"),
            ("sale_parse_error", "Sale Parse Error"),
            ("plu_uploaded", "PLU Uploaded"),
            ("plu_mismatch", "PLU Mismatch"),
            ("label_generated", "Label Generated"),
            ("manual_reset", "Manual Reset"),
            ("unexpected_sale", "Unexpected Sale"),
        ],
        required=True,
        index=True,
    )
    device_id = fields.Many2one("groundup.scale.device", index=True, ondelete="set null")
    payload_json = fields.Text(help="Full event payload as JSON")
    entry_hash = fields.Char(size=64, index=True, help="SHA-256 hash of this entry")
    prev_hash = fields.Char(size=64, help="SHA-256 hash of previous entry (chain link)")
    hub_timestamp = fields.Datetime(help="Timestamp from the Hub (UTC)")

    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("event_type", "device_id")
    def _compute_display_name(self):
        for rec in self:
            device = rec.device_id.name if rec.device_id else "?"
            rec.display_name = f"[{device}] {rec.event_type or '?'}"

    @api.model
    def ingest_hub_event(self, vals):
        """Called by the Hub (or a cron) to mirror audit log entries into Odoo."""
        return self.create(vals)
