from flight_search import FlightSearcher


def _airports():
    return [
        {
            "code": "JFK",
            "name": "John F. Kennedy International",
            "city": "New York",
            "country": "US",
            "timezone": "America/New_York",
        },
        {
            "code": "ORD",
            "name": "Chicago O'Hare",
            "city": "Chicago",
            "country": "US",
            "timezone": "America/Chicago",
        },
        {
            "code": "DFW",
            "name": "Dallas Fort Worth",
            "city": "Dallas",
            "country": "US",
            "timezone": "America/Chicago",
        },
        {
            "code": "LAX",
            "name": "Los Angeles International",
            "city": "Los Angeles",
            "country": "US",
            "timezone": "America/Los_Angeles",
        },
    ]


def _flights():
    return [
        {
            "flightNumber": "SP100",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "JFK",
            "destination": "LAX",
            "departureTime": "2024-03-15T08:00:00",
            "arrivalTime": "2024-03-15T11:00:00",
            "price": 200.00,
        },
        {
            "flightNumber": "SP200",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "JFK",
            "destination": "ORD",
            "departureTime": "2024-03-15T07:00:00",
            "arrivalTime": "2024-03-15T08:30:00",
            "price": 90.00,
        },
        {
            "flightNumber": "SP201",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "ORD",
            "destination": "LAX",
            "departureTime": "2024-03-15T09:30:00",
            "arrivalTime": "2024-03-15T11:30:00",
            "price": 120.00,
        },
        {
            "flightNumber": "SP300",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "JFK",
            "destination": "ORD",
            "departureTime": "2024-03-15T06:00:00",
            "arrivalTime": "2024-03-15T07:00:00",
            "price": 80.00,
        },
        {
            "flightNumber": "SP301",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "ORD",
            "destination": "DFW",
            "departureTime": "2024-03-15T08:00:00",
            "arrivalTime": "2024-03-15T10:00:00",
            "price": 70.00,
        },
        {
            "flightNumber": "SP302",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "DFW",
            "destination": "LAX",
            "departureTime": "2024-03-15T11:00:00",
            "arrivalTime": "2024-03-15T12:30:00",
            "price": 95.00,
        },
        {
            "flightNumber": "SP400",
            "airline": "SkyPath Airways",
            "aircraft": "A320",
            "origin": "ORD",
            "destination": "JFK",
            "departureTime": "2024-03-15T09:45:00",
            "arrivalTime": "2024-03-15T12:30:00",
            "price": 100.00,
        },
    ]


def test_search_returns_itineraries_sorted_by_total_duration():
    searcher = FlightSearcher(_flights(), _airports())
    itineraries = searcher.search("JFK", "LAX", "2024-03-15")

    assert len(itineraries) >= 2
    durations = [itinerary["totalDuration"] for itinerary in itineraries]
    assert durations == sorted(durations)


def test_search_allows_up_to_two_stops():
    searcher = FlightSearcher(_flights(), _airports())
    itineraries = searcher.search("JFK", "LAX", "2024-03-15")

    assert any(itinerary["stops"] == 2 for itinerary in itineraries)
    assert all(itinerary["stops"] <= 2 for itinerary in itineraries)


def test_search_avoids_cycles_in_paths():
    searcher = FlightSearcher(_flights(), _airports())
    itineraries = searcher.search("JFK", "LAX", "2024-03-15")

    for itinerary in itineraries:
        visited = []
        for segment in itinerary["segments"]:
            visited.append(segment["departure"]["airport"])
        visited.append(itinerary["segments"][-1]["arrival"]["airport"])
        assert len(visited) == len(set(visited))
