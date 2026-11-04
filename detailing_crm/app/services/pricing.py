"""Dynamic quote pricing: base service x vehicle-size multiplier.

This is a QUOTE table for the booking page, not a payment charge.
Owner decision 2026-11-04: no deposit, no payment gate. Final price is
confirmed in person after vehicle condition is seen -- the same honesty
rule the better competitors state publicly.
"""
VEHICLE_SIZE_MULTIPLIER = {
    "coupe": 1.0, "sedan": 1.0, "small_suv": 1.15,
    "full_suv": 1.3, "truck": 1.25, "3row": 1.35, "van": 1.35,
}
SERVICE_CATALOG = {
    "Standard Detail": {"base": 250.00, "hours": 4},
    "Interior Detail": {"base": 180.00, "hours": 3},
    "Exterior Detail": {"base": 150.00, "hours": 2},
    "Paint Correction": {"base": 650.00, "hours": 6},
    "Multi-Stage Paint Correction & Ceramic": {"base": 1650.00, "hours": 8},
    "Ceramic Coating": {"base": 1400.00, "hours": 6},
    "Ceramic Maintenance": {"base": 199.00, "hours": 2},
    "Seasonal Decontamination": {"base": 225.00, "hours": 3},
}
DEFAULT_SERVICE = {"base": 300.00, "hours": 4}

def quote(service_type: str, vehicle_size: str = "sedan") -> dict:
    svc = SERVICE_CATALOG.get(service_type, DEFAULT_SERVICE)
    mult = VEHICLE_SIZE_MULTIPLIER.get((vehicle_size or "sedan").lower(), 1.0)
    return {"service_type": service_type, "vehicle_size": vehicle_size,
            "estimated_price": round(svc["base"] * mult, 2),
            "estimated_duration_hours": svc["hours"],
            "note": "Estimate only. Final price confirmed after in-person condition check. No deposit required."}
