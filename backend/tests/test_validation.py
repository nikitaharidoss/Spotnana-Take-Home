from validation import (
    airport_exists,
    validate_connection,
    validate_search_input,
)


def test_validate_search_input_accepts_valid_payload():
    result = validate_search_input("JFK", "LAX", "2024-03-15")
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_search_input_rejects_invalid_values():
    result = validate_search_input("JFK", "JFK", "15-03-2024")
    assert result["valid"] is False
    assert "ERROR: Origin and destination cannot be the same." in result["errors"]
    assert "ERROR: Date must be in YYYY-MM-DD format." in result["errors"]


def test_validate_search_input_rejects_early_date():
    result = validate_search_input("JFK", "LAX", "2024-03-14")
    assert result["valid"] is False
    assert "ERROR: Date must be on or after 2024-03-15." in result["errors"]


def test_validate_connection_enforces_domestic_minimum_layover():
    airport_map = {
        "JFK": {"country": "US"},
        "ORD": {"country": "US"},
        "LAX": {"country": "US"},
    }
    arrival_flight = {
        "origin": "JFK",
        "destination": "ORD",
        "arrivalTime": "2024-03-15T10:00:00",
    }
    departing_flight = {
        "origin": "ORD",
        "destination": "LAX",
        "departureTime": "2024-03-15T10:44:00",
    }

    result = validate_connection(arrival_flight, departing_flight, airport_map, "2024-03-15")
    assert result["valid"] is False
    assert "Insufficient layover" in result["reason"]


def test_validate_connection_enforces_international_minimum_layover():
    airport_map = {
        "JFK": {"country": "US"},
        "LHR": {"country": "GB"},
        "CDG": {"country": "FR"},
    }
    arrival_flight = {
        "origin": "JFK",
        "destination": "LHR",
        "arrivalTime": "2024-03-15T10:00:00",
    }
    departing_flight = {
        "origin": "LHR",
        "destination": "CDG",
        "departureTime": "2024-03-15T11:25:00",
    }

    result = validate_connection(arrival_flight, departing_flight, airport_map, "2024-03-15")
    assert result["valid"] is False
    assert "Insufficient layover" in result["reason"]


def test_validate_connection_rejects_excessive_layover():
    airport_map = {
        "JFK": {"country": "US"},
        "ORD": {"country": "US"},
        "LAX": {"country": "US"},
    }
    arrival_flight = {
        "origin": "JFK",
        "destination": "ORD",
        "arrivalTime": "2024-03-15T08:00:00",
    }
    departing_flight = {
        "origin": "ORD",
        "destination": "LAX",
        "departureTime": "2024-03-15T15:00:00",
    }

    result = validate_connection(arrival_flight, departing_flight, airport_map, "2024-03-15")
    assert result["valid"] is False
    assert "Excessive layover" in result["reason"]


def test_airport_exists_checks_membership():
    airport_map = {"JFK": {}, "LAX": {}}
    assert airport_exists("JFK", airport_map) is True
    assert airport_exists("XXX", airport_map) is False
