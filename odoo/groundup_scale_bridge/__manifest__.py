{
    'name': 'GroundUp Scale Bridge',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Bridge between CAS ER-Plus scales and Odoo POS via GroundUp Hub',
    'description': """
GroundUp Scale Bridge
=====================

Connects CAS ER-Plus price-computing scales to Odoo via
the GroundUp Scale Hub (Raspberry Pi / CM4).

**Architecture:**
  - Scale is the sole authority for weight and price computation
  - Hub is a controlled, allowlist-based communication bridge
  - Odoo POS only receives finished sale data (no price computation)

**Features:**
  - PLU management and sync to scale via Hub
  - Append-only audit log mirroring from Hub
  - Scale device registry
  - GS1 Digital Link configuration per product
""",
    'author': 'Ground UP GmbH',
    'website': 'https://www.bodenkraft.com',
    'depends': [
        'base',
        'product',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/scale_device_views.xml',
        'views/scale_log_views.xml',
        'views/scale_plu_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
