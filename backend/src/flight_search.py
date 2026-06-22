from datetime import datetime
import pytz
from collections import defaultdict
from validation import validate_connection
from utils import format_time, format_duration

MAX_STOPS = 2


class FlightSearcher:
    """Search for flights with direct and connecting routes using DFS."""

    def __init__(self, flights, airports):
        self.airports = airports
        self.airport_map = {airport['code']: airport for airport in airports}

        # Adjacency map: origin airport → list of valid flights departing from it.
        # This replaces O(N) linear scans through self.flights in inner loops.
        self.flights_by_origin = defaultdict(list)
        for flight in flights:
            if (flight['origin'] in self.airport_map
                    and flight['destination'] in self.airport_map):
                self.flights_by_origin[flight['origin']].append(flight)

    def search(self, origin, destination, date):
        """Search for itineraries up to MAX_STOPS stops using DFS."""
        itineraries = []
        # Seed DFS with flights departing from origin on the search date.
        seed_flights = [
            f for f in self.flights_by_origin[origin]
            if f['departureTime'].startswith(date)
        ]
        for first_flight in seed_flights:
            self._dfs(
                current_flight=first_flight,
                destination=destination,
                date=date,
                path=[first_flight],
                visited={origin},
                itineraries=itineraries,
            )
        itineraries.sort(key=lambda x: x['totalDuration'])
        return itineraries

    def _dfs(self, current_flight, destination, date, path, visited, itineraries):
        """
        Recursively explore the flight graph depth-first.

        - Appends a completed itinerary when destination is reached.
        - Prunes branches that exceed MAX_STOPS or revisit airports.
        """
        current_dest = current_flight['destination']

        if current_dest == destination:
            itineraries.append(self._build_itinerary(path))
            return  # Destination reached; don't extend further.

        # Prune: already at MAX_STOPS intermediate airports.
        if len(path) > MAX_STOPS:
            return

        for next_flight in self.flights_by_origin[current_dest]:
            next_dest = next_flight['destination']

            # Avoid revisiting airports already in the path.
            if next_dest in visited and next_dest != destination:
                continue

            # Validate layover rules between current and next flight.
            if not validate_connection(current_flight, next_flight, self.airport_map, date)['valid']:
                continue

            visited.add(current_dest)
            path.append(next_flight)

            self._dfs(next_flight, destination, date, path, visited, itineraries)

            path.pop()
            visited.discard(current_dest)

    
    def _build_itinerary(self, flight_segments):
        """Build itinerary from flight segments"""
        segments = []
        total_duration_minutes = 0
        total_price = 0
        
        for i, flight in enumerate(flight_segments):
            origin_airport = self.airport_map[flight['origin']]
            dest_airport = self.airport_map[flight['destination']]
            
            # Parse times in local airport timezone
            tz_origin = pytz.timezone(origin_airport['timezone'])
            tz_dest = pytz.timezone(dest_airport['timezone'])
            
            depart_local = datetime.strptime(
                flight['departureTime'],
                '%Y-%m-%dT%H:%M:%S'
            )
            depart_local = tz_origin.localize(depart_local)
            depart_utc = depart_local.astimezone(pytz.utc)
            
            arrive_local = datetime.strptime(
                flight['arrivalTime'],
                '%Y-%m-%dT%H:%M:%S'
            )
            arrive_local = tz_dest.localize(arrive_local)
            arrive_utc = arrive_local.astimezone(pytz.utc)
            
            flight_duration_minutes = int((arrive_utc - depart_utc).total_seconds() / 60)
            
            segment = {
                'flightNumber': flight['flightNumber'],
                'airline': flight['airline'],
                'aircraft': flight['aircraft'],
                'departure': {
                    'airport': flight['origin'],
                    'airportName': origin_airport['name'],
                    'time': format_time(flight['departureTime'], origin_airport['timezone']),
                    'isoTime': flight['departureTime'],
                    'city': origin_airport['city'],
                    'country': origin_airport['country']
                },
                'arrival': {
                    'airport': flight['destination'],
                    'airportName': dest_airport['name'],
                    'time': format_time(flight['arrivalTime'], dest_airport['timezone']),
                    'isoTime': flight['arrivalTime'],
                    'city': dest_airport['city'],
                    'country': dest_airport['country']
                },
                'duration': flight_duration_minutes
            }
            
            segments.append(segment)
            total_duration_minutes += flight_duration_minutes
            total_price += float(flight['price'])
            
            # Add layover if not last segment
            if i < len(flight_segments) - 1:
                next_flight = flight_segments[i + 1]
                # Both times are at the same connection airport (same timezone),
                # so naive subtraction is correct — no UTC conversion needed.
                next_depart = datetime.strptime(next_flight['departureTime'], '%Y-%m-%dT%H:%M:%S')
                arrive = datetime.strptime(flight['arrivalTime'], '%Y-%m-%dT%H:%M:%S')
                layover_minutes = int((next_depart - arrive).total_seconds() / 60)
                
                segments[i]['layover'] = {
                    'airport': flight['destination'],
                    'duration': layover_minutes,
                    'durationFormatted': format_duration(layover_minutes)
                }
                
                total_duration_minutes += layover_minutes
        
        return {
            'segments': segments,
            'totalDuration': total_duration_minutes,
            'totalDurationFormatted': format_duration(total_duration_minutes),
            'totalPrice': f'{total_price:.2f}',
            'stops': len(flight_segments) - 1
        }


# Backward-compatible function wrapper for existing code
def search_flights(origin, destination, date, flights, airports):
    """Legacy function wrapper - use FlightSearcher class directly"""
    searcher = FlightSearcher(flights, airports)
    return searcher.search(origin, destination, date)
