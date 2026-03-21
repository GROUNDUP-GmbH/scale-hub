"""
GroundUp Scale Hub – Zebra ZPL Label Generator

Generates ZPL II commands for self-adhesive labels on Zebra printers.
Contains human-readable text (product, weight, price) plus a QR code
encoding the GS1 Digital Link.

Label dimensions assume 60 × 40 mm (adjustable via constants).
"""
from __future__ import annotations


LABEL_WIDTH_DOTS = 480  # 60 mm @ 203 dpi
LABEL_HEIGHT_DOTS = 320  # 40 mm @ 203 dpi


def build_zpl_label(
    *,
    product_name: str,
    weight_kg: float,
    unit_price: float,
    total_price: float,
    digital_link: str,
    gtin: str | None = None,
    lot: str | None = None,
    expiry: str | None = None,
    currency: str = "EUR",
) -> str:
    """
    Generate a complete ZPL II label with QR code.

    The QR code encodes the GS1 Digital Link URL.
    Human-readable fields show weight, price and product info
    as required for metrological transparency.
    """
    lot_text = lot or ""
    exp_text = expiry or ""
    gtin_text = gtin or ""

    zpl = f"""^XA
^CI28
^CF0,28
^FO30,20^FD{product_name[:30]}^FS
^CF0,22
^FO30,60^FDGewicht: {weight_kg:.3f} kg^FS
^FO30,90^FDPreis/kg: {unit_price:.2f} {currency}^FS
^CF0,30
^FO30,125^FDGesamt: {total_price:.2f} {currency}^FS
^CF0,18"""

    if gtin_text:
        zpl += f"\n^FO30,165^FDGTIN: {gtin_text}^FS"
    if lot_text:
        zpl += f"\n^FO30,190^FDCharge: {lot_text}^FS"
    if exp_text:
        zpl += f"\n^FO30,215^FDMHD: {exp_text}^FS"

    zpl += f"""
^FO300,20^BQN,2,5
^FDLA,{digital_link}^FS
^XZ"""

    return zpl
