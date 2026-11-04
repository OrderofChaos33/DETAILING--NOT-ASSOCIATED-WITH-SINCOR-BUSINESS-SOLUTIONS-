import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "detailing_crm"))
from datetime import datetime, timedelta
from app.services.pricing import quote
from app.services.calendar_logic import is_slot_available
from app.services.nurture import due_new_lead_messages, due_reactivation

def test_quote_scales_with_vehicle_size():
    assert quote("Standard Detail", "sedan")["estimated_price"] == 250.00
    assert quote("Standard Detail", "full_suv")["estimated_price"] == 325.00
    assert quote("Ceramic Coating", "coupe")["estimated_duration_hours"] == 6

def test_calendar_overlap_with_buffer():
    start = datetime(2026, 11, 10, 8, 0)
    existing = [(start, 4)]  # 8:00 + 4h + 30m buffer blocks until 12:30
    assert not is_slot_available(existing, datetime(2026, 11, 10, 11, 0), 2)
    assert not is_slot_available(existing, datetime(2026, 11, 10, 12, 0), 2)
    assert is_slot_available(existing, datetime(2026, 11, 10, 13, 0), 2)
    assert is_slot_available(existing, datetime(2026, 11, 11, 8, 0), 4)

def test_new_lead_sequence_timing():
    t0 = datetime(2026, 11, 4, 12, 0)
    assert len(due_new_lead_messages(t0, t0)) == 1
    assert len(due_new_lead_messages(t0, t0 + timedelta(days=1, minutes=1))) == 3
    assert len(due_new_lead_messages(t0, t0 + timedelta(days=8))) == 5

def test_reactivation_ceramic_six_months():
    t0 = datetime(2026, 5, 1, 10, 0)
    assert due_reactivation("Ceramic Coating", t0, t0 + timedelta(days=90)) is None
    assert due_reactivation("Ceramic Coating", t0, t0 + timedelta(days=181)) is not None
