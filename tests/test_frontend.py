"""End-to-end: the customer page loads from the API app and the exact call
sequence app.js makes (quote -> availability -> create-appointment) succeeds."""

def test_page_loads_with_exact_facts_and_security_headers(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    for fact in ("Clinton Auto Detailing", "$250", "Free Pickup", "Licensed",
                 "5 stars", "815-718-8936", "715 Park Pl", "No deposit"):
        assert fact in html, fact
    assert "4.9" not in html  # owner's rule: say "5 stars", never a decimal
    assert "SINCOR" not in html.upper()  # brand separation, always
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "content-security-policy" in r.headers

def test_assets_served(client):
    assert client.get("/styles.css").status_code == 200
    js = client.get("/app.js")
    assert js.status_code == 200
    assert "/api/v1/bookings/create-appointment" in js.text
    assert "/api/v1/bookings/availability" in js.text

def test_booking_flow_exactly_as_the_page_does_it(client):
    q = client.post("/api/v1/bookings/quote", json={"service_type": "Standard Detail", "vehicle_size": "truck"})
    assert q.status_code == 200 and q.json()["estimated_price"] == 312.50
    av = client.get("/api/v1/bookings/availability", params={"date": "2026-11-20", "service_type": "Standard Detail"})
    assert av.status_code == 200
    open_slots = [s for s in av.json()["slots"] if s["available"]]
    assert open_slots, "expected at least one open slot on an empty calendar"
    body = {"name": "Page Tester", "phone": "555-0199", "vehicle_year": 2021, "vehicle_make": "Ram",
            "vehicle_model": "1500", "vehicle_size": "truck", "service_type": "Standard Detail",
            "scheduled_time": open_slots[0]["start"], "source": "website",
            "notes": "Free pickup & delivery requested; Pet hair"}
    r = client.post("/api/v1/bookings/create-appointment", json=body)
    assert r.status_code == 201, r.text
    j = r.json()
    assert j["status"] == "confirmed" and j["deposit_required"] is False and j["total_price"] == 312.50
