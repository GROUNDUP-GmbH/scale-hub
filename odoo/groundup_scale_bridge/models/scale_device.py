from odoo import api, fields, models


class GroundupScaleDevice(models.Model):
    _name = "groundup.scale.device"
    _description = "GroundUp Scale Device"
    _order = "name"

    name = fields.Char(required=True, help="Human-readable device name, e.g. 'Marktstand Wien CAS-01'")
    device_id = fields.Char(
        required=True,
        index=True,
        help="Unique identifier matching the Hub configuration",
    )
    hub_url = fields.Char(
        string="Hub URL",
        required=True,
        default="http://localhost:8420",
        help="Base URL of the GroundUp Scale Hub for this device",
    )
    scale_model = fields.Selection(
        [
            ("cas_erplus", "CAS ER-Plus"),
            ("cas_erplus_pole", "CAS ER-Plus (Pole)"),
            ("other", "Other"),
        ],
        default="cas_erplus",
        required=True,
    )
    serial_port_a = fields.Char(
        default="/dev/ttyUSB0",
        help="RS-232 Port A (Full Duplex) for PLU commands",
    )
    serial_port_b = fields.Char(
        default="/dev/ttyUSB1",
        help="RS-232 Port B (TX only) for sale data from scale",
    )
    baudrate = fields.Integer(default=9600)
    active = fields.Boolean(default=True)
    location = fields.Char(help="Physical location, e.g. 'Naschmarkt Stand 42'")
    notes = fields.Text()
    country_code = fields.Char(
        size=2,
        default="AT",
        help="ISO 3166-1 alpha-2 country code. Determines which compliance.yaml is loaded.",
    )

    plu_ids = fields.One2many("groundup.scale.plu", "device_id", string="PLU Mappings")
    log_ids = fields.One2many("groundup.scale.log", "device_id", string="Audit Logs")
    log_count = fields.Integer(compute="_compute_log_count", string="Log Entries")

    _sql_constraints = [
        ("device_id_unique", "UNIQUE(device_id)", "Device ID must be unique."),
    ]

    @api.depends("log_ids")
    def _compute_log_count(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)
