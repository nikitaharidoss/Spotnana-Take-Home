const moment = require('moment-timezone');
const { localToUTC, minutesBetween } = require('./utils');

const MIN_LAYOVER_DOMESTIC = 45; // minutes
const MAX_LAYOVER = 360; // 6 hours
const MIN_LAYOVER_INTERNATIONAL = 90; // minutes

// Determine if connection is domestic
function isDomestic(countryFrom, countryTo) {
  return countryFrom === countryTo;
}

// Determine minimum layover required based on connection type
function getMinLayover(countryFrom, countryTo) {
  return isDomestic(countryFrom, countryTo) ? MIN_LAYOVER_DOMESTIC : MIN_LAYOVER_INTERNATIONAL;
}

// Validate a potential connection between two flights
function validateConnection(
  arrivalFlight,
  departingFlight,
  airportMap,
  searchDate
) {
  // Flights must be at same airport
  if (arrivalFlight.destination !== departingFlight.origin) {
    return { valid: false, reason: 'Airports do not match' };
  }

  const airport = airportMap[arrivalFlight.destination];
  const timezone = airport.timezone;

  // Parse times in airport timezone
  const arrivalTimeLocal = moment.tz(
    arrivalFlight.arrivalTime,
    'YYYY-MM-DDTHH:mm:ss',
    timezone
  );
  const departureTimeLocal = moment.tz(
    departingFlight.departureTime,
    'YYYY-MM-DDTHH:mm:ss',
    timezone
  );

  // Calculate layover duration
  const layoverMinutes = minutesBetween(arrivalTimeLocal, departureTimeLocal);

  // Check min layover
  const minRequired = getMinLayover(
    airport.country,
    airport.country  // Same airport, so both in same country
  );
  
  // Actually check based on countries of origin/destination of the flights
  const originCountry = airportMap[arrivalFlight.origin].country;
  const destCountry = airportMap[departingFlight.destination].country;
  const connectionCountry = airport.country;
  
  const minLayoverRequired = isDomestic(originCountry, destCountry)
    ? MIN_LAYOVER_DOMESTIC
    : MIN_LAYOVER_INTERNATIONAL;

  if (layoverMinutes < minLayoverRequired) {
    return {
      valid: false,
      reason: `Insufficient layover: ${layoverMinutes}m < ${minLayoverRequired}m required`
    };
  }

  // Check max layover
  if (layoverMinutes > MAX_LAYOVER) {
    return {
      valid: false,
      reason: `Excessive layover: ${layoverMinutes}m > ${MAX_LAYOVER}m`
    };
  }

  return {
    valid: true,
    layoverMinutes,
    minLayoverRequired
  };
}

// Validate search inputs
function validateSearchInput(origin, destination, date) {
  const errors = [];

  if (!origin || origin.length !== 3) {
    errors.push('Origin must be a valid 3-letter airport code');
  }

  if (!destination || destination.length !== 3) {
    errors.push('Destination must be a valid 3-letter airport code');
  }

  if (origin && destination && origin === destination) {
    errors.push('Origin and destination cannot be the same');
  }

  if (!date || !moment(date, 'YYYY-MM-DD', true).isValid()) {
    errors.push('Date must be in YYYY-MM-DD format');
  }

  if (!date || moment(date, 'YYYY-MM-DD').isBefore(moment('2024-03-15'))) {
    errors.push('Date must be on or after 2024-03-15');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

// Check if airport exists
function airportExists(code, airportMap) {
  return code in airportMap;
}

module.exports = {
  validateConnection,
  validateSearchInput,
  airportExists,
  isDomestic,
  MIN_LAYOVER_DOMESTIC,
  MAX_LAYOVER,
  MIN_LAYOVER_INTERNATIONAL,
  getMinLayover
};
