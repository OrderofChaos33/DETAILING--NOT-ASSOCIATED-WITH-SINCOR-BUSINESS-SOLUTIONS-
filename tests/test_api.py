def test_health_and_security_headers(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["shop"] == "Clinton Auto Detailing"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"

def test_booking_no_deposit_and_overlap_rejected(client):
    body = {"name": "Test Driver", "phone": "555-0100", "vehicle_year": 2022, "vehicle_make": "Ford",
            "vehicle_model": "Mustang", "vehicle_size": "coupe", "service_type": "Standard Detail",
            "scheduled_time": "2026-11-12T08:00:00"}
    r = client.post("/api/v1/bookings/create-appointment", json=body)
    assert r.status_code == 201, r.text
    j = r.json(); assert j["deposit_required"] is False and j["total_price"] == 250.00 and j["sms_sent"] is False
    r2 = client.post("/api/v1/bookings/create-appointment", json={**body, "phone": "555-0101", "scheduled_time": "2026-11-12T10:00:00"})
    assert r2.status_code == 409

def test_lead_capture_and_missed_call(client):
    r = client.post("/api/v1/webhooks/lead-capture", json={"phone": "555-0200", "source": "meta_ad", "name": "Lead One"})
    assert r.status_code == 201 and r.json()["sms_sent"] is False
    r = client.post("/api/v1/webhooks/missed-call", json={"phone": "555-0201", "source": "phone"})
    assert r.status_code == 201 and r.json()["action"] == "missed_call_text_back"

def test_quote_endpoint(client):
    r = client.post("/api/v1/bookings/quote", json={"service_type": "Ceramic Coating", "vehicle_size": "full_suv"})
    assert r.status_code == 200 and r.json()["estimated_price"] == 1820.00
