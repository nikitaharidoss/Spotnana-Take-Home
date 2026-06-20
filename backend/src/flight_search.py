from datetime import datetime
import pytz
from validation import validate_connection
from utils import format_time, format_duration


class FlightSearcher:
    """Search for flights with direct and connecting routes"""
    
    def __init__(self, flights, airports):
        self.flights = flights
        self.airports = airports
        self.airport_map = {airport['code']: airport for airport in airports}
    
    def search(self, origin, destination, date):
        """Search for flights with connections"""
        available_flights = self._get_flights_for_date(origin, date)
        itineraries = []

        # 1. Direct flights
        itineraries.extend(self._find_direct_flights(available_flights, destination))
        
        # 2. One-stop connections
        itineraries.extend(self._find_one_stop_flights(available_flights, destination, date))
        
        # 3. Two-stop connections
        itineraries.extend(self._find_two_stop_flights(available_flights, origin, destination, date))
        
        # Sort by total duration
        itineraries.sort(key=lambda x: x['totalDuration'])
        
        return itineraries
    
    def search_2(self, origin, destination, date):
        """Search for flights with at most two stops"""
        # This method currently delegates to the main search method, which already handles up to two stops
        # and returns the same results

        return self.search(origin, destination, date)
    
    def _get_flights_for_date(self, depart_airport_code, search_date):
        """Get flights departing from airport on search date"""
        result = []
        for flight in self.flights:
            if flight['origin'] != depart_airport_code:
                continue
            
            if flight['origin'] not in self.airport_map or flight['destination'] not in self.airport_map:
                continue
            
            tz = pytz.timezone(self.airport_map[flight['origin']]['timezone'])
            depart_local = datetime.strptime(flight['departureTime'], '%Y-%m-%dT%H:%M:%S')
            depart_local = tz.localize(depart_local)
            
            if depart_local.strftime('%Y-%m-%d') == search_date:
                result.append(flight)
        
        return result
    
    def _find_direct_flights(self, available_flights, destination):
        """Find direct flights to destination"""
        itineraries = []
        for flight in available_flights:
            if flight['destination'] == destination:
                itinerary = self._build_itinerary([flight])
                itineraries.append(itinerary)
        return itineraries
    
    def _find_one_stop_flights(self, available_flights, destination, date):
        """Find one-stop connecting flights"""
        itineraries = []
        for flight1 in available_flights:
            stop1 = flight1['destination']
            if stop1 == destination:
                continue
            
            connecting_flights = [
                f for f in self.flights
                if f['origin'] == stop1
                and f['destination'] == destination
                and f['origin'] in self.airport_map
                and f['destination'] in self.airport_map
            ]
            
            for flight2 in connecting_flights:
                validation = validate_connection(flight1, flight2, self.airport_map, date)
                if validation['valid']:
                    itinerary = self._build_itinerary([flight1, flight2])
                    itineraries.append(itinerary)
        
        return itineraries
    
    def _find_two_stop_flights(self, available_flights, origin, destination, date):
        """Find two-stop connecting flights"""
        itineraries = []
        for flight1 in available_flights:
            stop1 = flight1['destination']
            if stop1 == destination:
                continue
            
            for flight2 in self.flights:
                if (flight2['origin'] != stop1
                    or flight2['destination'] == origin
                    or flight2['destination'] == destination
                    or flight2['origin'] not in self.airport_map
                    or flight2['destination'] not in self.airport_map):
                    continue
                
                validation1 = validate_connection(flight1, flight2, self.airport_map, date)
                if not validation1['valid']:
                    continue
                
                stop2 = flight2['destination']
                
                for flight3 in self.flights:
                    if (flight3['origin'] != stop2
                        or flight3['destination'] != destination
                        or flight3['origin'] not in self.airport_map
                        or flight3['destination'] not in self.airport_map):
                        continue
                    
                    validation2 = validate_connection(flight2, flight3, self.airport_map, date)
                    if validation2['valid']:
                        itinerary = self._build_itinerary([flight1, flight2, flight3])
                        itineraries.append(itinerary)
        
        return itineraries
    
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
                next_tz = pytz.timezone(self.airport_map[next_flight['origin']]['timezone'])
                next_depart_local = datetime.strptime(
                    next_flight['departureTime'],
                    '%Y-%m-%dT%H:%M:%S'
                )
                next_depart_local = next_tz.localize(next_depart_local)
                next_depart_utc = next_depart_local.astimezone(pytz.utc)
                
                layover_minutes = int((next_depart_utc - arrive_utc).total_seconds() / 60)
                
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
