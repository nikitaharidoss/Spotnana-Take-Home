from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_health_endpoint_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_airports_endpoint_returns_airport_list():
    response = client.get("/api/airports")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) > 0
    assert "code" in payload[0]


def test_search_endpoint_returns_itineraries_for_valid_request():
    response = client.post(
        "/api/search",
        json={"origin": "JFK", "destination": "LAX", "date": "2024-03-15"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "itineraries" in payload
    assert "count" in payload


def test_search_endpoint_rejects_invalid_airport():
    response = client.post(
        "/api/search",
        json={"origin": "XXX", "destination": "LAX", "date": "2024-03-15"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] == "Invalid airport code"
    assert any("Airport XXX not found" in detail for detail in payload["details"])


def test_search_endpoint_rejects_invalid_search_payload():
    response = client.post(
        "/api/search",
        json={"origin": "JFK", "destination": "JFK", "date": "2024-03-15"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] == "Invalid search parameters."
    assert "ERROR: Origin and destination cannot be the same." in payload["details"]


def test_search_endpoint_surfaces_internal_error(monkeypatch):
    def failing_search(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(main.searcher, "search", failing_search)
    response = client.post(
        "/api/search",
        json={"origin": "JFK", "destination": "LAX", "date": "2024-03-15"},
    )
    assert response.status_code == 500
    payload = response.json()
    assert payload["error"] == "Internal server error"
    assert payload["details"] == ["boom"]
