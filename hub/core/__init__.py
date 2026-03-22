"""
Certified Core — legally relevant software (WELMEC 7.2 Extension S).

This package contains ALL metrologically relevant code:
- Serial communication with the scale
- Price calculation (Tier 0)
- Audit log (hash-chained, append-only)
- Transaction state machine
- Sealed parameter store
- Software identification

RULE: No imports from hub.periphery are allowed in this package.
"""
