from datetime import datetime
import pytz
from validation import validate_connection
from utils import format_time, format_duration, minutes_between

def search_flights(origin, destination, date, flights, airports):
    """Search for flights with connections"""
    airport_map = {airport['code']: airport for airport in airports}
    
    def get_flights_for_date(depart_airport_code, search_date):
        """Get flights departing from airport on search date (by local departure time)"""
        result = []
        for flight in flights:
            if flight['origin'] != depart_airport_code:
                continue
            
            if flight['origin'] not in airport_map or flight['destination'] not in airport_map:
                continue
            
            tz = pytz.timezone(airport_map[flight['origin']]['timezone'])
            depart_local = datetime.strptime(flight['departureTime'], '%Y-%m-%dT%H:%M:%S')
            depart_local = tz.localize(depart_local)
            
            if depart_local.strftime('%Y-%m-%d') == search_date:
                result.append(flight)
        
        return result
    
    # Get flights from origin on this date
    available_flights = get_flights_for_date(origin, date)
    itineraries = []
    
    # 1. Direct flights
    for flight in available_flights:
        if flight['destination'] == destination:
            itinerary = build_itinerary([flight], airport_map)
            itineraries.append(itinerary)
    
    # 2. One-stop connections
    for flight1 in available_flights:
        stop1 = flight1['destination']
        if stop1 == destination:
            continue
        
        connecting_flights = [
            f for f in flights
            if f['origin'] == stop1
            and f['destination'] == destination
            and f['origin'] in airport_map
            and f['destination'] in airport_map
        ]
        
        for flight2 in connecting_flights:
            validation = validate_connection(flight1, flight2, airport_map, date)
            if validation['valid']:
                itinerary = build_itinerary([flight1, flight2], airport_map)
                itineraries.append(itinerary)
    
    # 3. Two-stop connections
    for flight1 in available_flights:
        stop1 = flight1['destination']
        if stop1 == destination:
            continue
        
        for flight2 in flights:
            if (flight2['origin'] != stop1
                or flight2['destination'] == origin
                or flight2['destination'] == destination
                or flight2['origin'] not in airport_map
                or flight2['destination'] not in airport_map):
                continue
            
            validation1 = validate_connection(flight1, flight2, airport_map, date)
            if not validation1['valid']:
                continue
            
            stop2 = flight2['destination']
            
            for flight3 in flights:
                if (flight3['origin'] != stop2
                    or flight3['destination'] != destination
                    or flight3['origin'] not in airport_map
                    or flight3['destination'] not in airport_map):
                    continue
                
                validation2 = validate_connection(flight2, flight3, airport_map, date)
                if validation2['valid']:
                    itinerary = build_itinerary([flight1, flight2, flight3], airport_map)
                    itineraries.append(itinerary)
    
    # Sort by total duration
    itineraries.sort(key=lambda x: x['totalDuration'])
    
    return itineraries

def build_itinerary(flight_segments, airport_map):
    """Build itinerary from flight segments"""
    segments = []
    total_duration_minutes = 0
    total_price = 0
    
    for i, flight in enumerate(flight_segments):
        origin_airport = airport_map[flight['origin']]
        dest_airport = airport_map[flight['destination']]
        
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
            next_tz = pytz.timezone(airport_map[next_flight['origin']]['timezone'])
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
