from datetime import datetime

MIN_LAYOVER_DOMESTIC = 45  # minutes
MAX_LAYOVER = 360  # 6 hours
MIN_LAYOVER_INTERNATIONAL = 90  # minutes


def validate_connection(arrival_flight, departing_flight, airport_map, search_date):
    """Validate a potential connection between two flights"""
    # Flights must be at same airport
    if arrival_flight['destination'] != departing_flight['origin']:
        return {'valid': False, 'reason': 'Airports do not match'}

    # Both times are already in the local time of the connection airport,
    # so naive datetime subtraction is correct — no timezone conversion needed.
    arrival_time = datetime.strptime(arrival_flight['arrivalTime'], '%Y-%m-%dT%H:%M:%S')
    departure_time = datetime.strptime(departing_flight['departureTime'], '%Y-%m-%dT%H:%M:%S')

    # Calculate layover duration
    layover_minutes = int((departure_time - arrival_time).total_seconds() / 60)
    
    # Determine connection type (domestic or international)
    origin_country = airport_map[arrival_flight['origin']]['country']
    dest_country = airport_map[departing_flight['destination']]['country']
    
    is_domestic = origin_country == dest_country
    min_layover_required = MIN_LAYOVER_DOMESTIC if is_domestic else MIN_LAYOVER_INTERNATIONAL
    
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
        errors.append('ERROR: Origin must be a valid 3-letter airport code.')
    
    if not destination or len(destination) != 3:
        errors.append('ERROR: Destination must be a valid 3-letter airport code.')
    
    if origin and destination and origin == destination:
        errors.append('ERROR: Origin and destination cannot be the same.')
    
    try:
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError):
        errors.append('ERROR: Date must be in YYYY-MM-DD format.')
        parsed_date = None
    
    if parsed_date and parsed_date < datetime(2024, 3, 15):
        errors.append('ERROR: Date must be on or after 2024-03-15.')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def airport_exists(code, airport_map):
    """Check if airport exists"""
    return code in airport_map
