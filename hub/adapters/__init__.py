"""Scale protocol adapters — one module per scale family.

Adapter inventory (Protocol Catalog families):
  1. cas_lp    — CAS LP (Tier 1, binary PLU, RS-232)
  2. cas_er    — CAS ER-Plus / AP (Tier 2, weight+price read-only, RS-232)
  3. cas_cl    — CAS CL (Tier 1, extended PLU, RS-232 + TCP/IP)
  4. digi_sm   — DIGI SM-100/120/300/5300 (Tier 1, Ethernet TCP/IP)
  5. mettler_tiger — Mettler Toledo Tiger (Tier 1, RS-232 + Ethernet)
  6. dibal     — DIBAL EPOS TISA (Tier 2+, price injection, RS-232)
  7. acom      — Acom NETS/PC (Tier 1, RS-232 + Ethernet)
  8. massa_k   — MASSA-K VPM/VP/Basic (Tier 1/2, RS-232 + Ethernet)
"""
