from datetime import datetime
import pytz

MIN_LAYOVER_DOMESTIC = 45  # minutes
MAX_LAYOVER = 360  # 6 hours
MIN_LAYOVER_INTERNATIONAL = 90  # minutes

def is_domestic(country_from, country_to):
    """Determine if connection is domestic"""
    return country_from == country_to

def get_min_layover(country_from, country_to):
    """Determine minimum layover required based on connection type"""
    return MIN_LAYOVER_DOMESTIC if is_domestic(country_from, country_to) else MIN_LAYOVER_INTERNATIONAL

def validate_connection(arrival_flight, departing_flight, airport_map, search_date):
    """Validate a potential connection between two flights"""
    # Flights must be at same airport
    if arrival_flight['destination'] != departing_flight['origin']:
        return {'valid': False, 'reason': 'Airports do not match'}
    
    airport = airport_map[arrival_flight['destination']]
    timezone = airport['timezone']
    
    # Parse times in airport timezone
    arrival_time_local = datetime.strptime(
        arrival_flight['arrivalTime'],
        '%Y-%m-%dT%H:%M:%S'
    )
    tz = pytz.timezone(timezone)
    arrival_time_local = tz.localize(arrival_time_local)
    
    departure_time_local = datetime.strptime(
        departing_flight['departureTime'],
        '%Y-%m-%dT%H:%M:%S'
    )
    departure_time_local = tz.localize(departure_time_local)
    
    # Calculate layover duration
    layover_minutes = int((departure_time_local - arrival_time_local).total_seconds() / 60)
    
    # Determine connection type (domestic or international)
    origin_country = airport_map[arrival_flight['origin']]['country']
    dest_country = airport_map[departing_flight['destination']]['country']
    
    min_layover_required = get_min_layover(origin_country, dest_country)
    
    # Check min layover
    if layover_minutes < min_layover_required:
        return {
            'valid': False,
            'reason': f'Insufficient layover: {layover_minutes}m < {min_layover_required}m required'
        }
    
    # Check max layover
    if layover_minutes > MAX_LAYOVER:
        return {
            'valid': False,
            'reason': f'Excessive layover: {layover_minutes}m > {MAX_LAYOVER}m'
        }
    
    return {
        'valid': True,
        'layover_minutes': layover_minutes,
        'min_layover_required': min_layover_required
    }

def validate_search_input(origin, destination, date):
    """Validate search inputs"""
    errors = []
    
    if not origin or len(origin) != 3:
        errors.append('Origin must be a valid 3-letter airport code')
    
    if not destination or len(destination) != 3:
        errors.append('Destination must be a valid 3-letter airport code')
    
    if origin and destination and origin == destination:
        errors.append('Origin and destination cannot be the same')
    
    try:
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError):
        errors.append('Date must be in YYYY-MM-DD format')
        parsed_date = None
    
    if parsed_date and parsed_date < datetime(2024, 3, 15):
        errors.append('Date must be on or after 2024-03-15')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def airport_exists(code, airport_map):
    """Check if airport exists"""
    return code in airport_map
