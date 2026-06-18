const moment = require('moment-timezone');
const { validateConnection, isDomestic } = require('./validation');
const { formatTime, formatDuration, minutesBetween } = require('./utils');

// Search for flights with connections
function searchFlights(origin, destination, date, flights, airports) {
  const airportMap = {};
  airports.forEach((airport) => {
    airportMap[airport.code] = airport;
  });

  // Get flights for a specific date (by departure date in local timezone)
  function getFlightsForDate(departAirportCode, searchDate) {
    return flights.filter((flight) => {
      if (!airportMap[flight.origin] || !airportMap[flight.destination]) {
        return false;
      }
      if (flight.origin !== departAirportCode) {
        return false;
      }
      const departLocal = moment.tz(
        flight.departureTime,
        'YYYY-MM-DDTHH:mm:ss',
        airportMap[flight.origin].timezone
      );
      return departLocal.format('YYYY-MM-DD') === searchDate;
    });
  }

  // Get available flights for a specific date from the origin
  const availableFlights = getFlightsForDate(origin, date);
  const itineraries = [];

  // 1. Direct flights
  availableFlights.forEach((flight) => {
    if (flight.destination === destination) {
      const itinerary = buildItinerary([flight], airportMap);
      itineraries.push(itinerary);
    }
  });

  // 2. One-stop connections (origin -> stop1 -> destination)
  availableFlights.forEach((flight1) => {
    const stop1 = flight1.destination;
    if (stop1 === destination) return; // Already handled by direct

    // Find connecting flights from stop1
    const connectingFlights = flights.filter(
      (f) =>
        f.origin === stop1 &&
        f.destination === destination &&
        airportMap[f.origin] &&
        airportMap[f.destination]
    );

    connectingFlights.forEach((flight2) => {
      const validation = validateConnection(flight1, flight2, airportMap, date);
      if (validation.valid) {
        const itinerary = buildItinerary([flight1, flight2], airportMap);
        itineraries.push(itinerary);
      }
    });
  });

  // 3. Two-stop connections (origin -> stop1 -> stop2 -> destination)
  availableFlights.forEach((flight1) => {
    const stop1 = flight1.destination;
    if (stop1 === destination) return;

    // Find flights from stop1 to potential stop2s
    flights.forEach((flight2) => {
      if (
        flight2.origin !== stop1 ||
        flight2.destination === origin ||
        flight2.destination === destination ||
        !airportMap[flight2.origin] ||
        !airportMap[flight2.destination]
      ) {
        return;
      }

      const validation1 = validateConnection(flight1, flight2, airportMap, date);
      if (!validation1.valid) return;

      const stop2 = flight2.destination;

      // Find flights from stop2 to destination
      flights.forEach((flight3) => {
        if (
          flight3.origin !== stop2 ||
          flight3.destination !== destination ||
          !airportMap[flight3.origin] ||
          !airportMap[flight3.destination]
        ) {
          return;
        }

        const validation2 = validateConnection(flight2, flight3, airportMap, date);
        if (validation2.valid) {
          const itinerary = buildItinerary([flight1, flight2, flight3], airportMap);
          itineraries.push(itinerary);
        }
      });
    });
  });

  // Sort by total duration
  itineraries.sort((a, b) => a.totalDuration - b.totalDuration);

  return itineraries;
}

function buildItinerary(flightSegments, airportMap) {
  const segments = [];
  let totalDurationMinutes = 0;
  let totalPrice = 0;

  for (let i = 0; i < flightSegments.length; i++) {
    const flight = flightSegments[i];
    const originAirport = airportMap[flight.origin];
    const destAirport = airportMap[flight.destination];

    // Parse times in local airport time
    const departLocal = moment.tz(
      flight.departureTime,
      'YYYY-MM-DDTHH:mm:ss',
      originAirport.timezone
    );
    const arriveLocal = moment.tz(
      flight.arrivalTime,
      'YYYY-MM-DDTHH:mm:ss',
      destAirport.timezone
    );

    // Calculate actual flight duration in UTC
    const departUTC = moment.tz(
      flight.departureTime,
      'YYYY-MM-DDTHH:mm:ss',
      originAirport.timezone
    ).utc();
    const arriveUTC = moment.tz(
      flight.arrivalTime,
      'YYYY-MM-DDTHH:mm:ss',
      destAirport.timezone
    ).utc();
    const flightDurationMinutes = arriveUTC.diff(departUTC, 'minutes');

    segments.push({
      flightNumber: flight.flightNumber,
      airline: flight.airline,
      aircraft: flight.aircraft,
      departure: {
        airport: flight.origin,
        airportName: originAirport.name,
        time: formatTime(flight.departureTime, originAirport.timezone),
        isoTime: flight.departureTime,
        city: originAirport.city,
        country: originAirport.country
      },
      arrival: {
        airport: flight.destination,
        airportName: destAirport.name,
        time: formatTime(flight.arrivalTime, destAirport.timezone),
        isoTime: flight.arrivalTime,
        city: destAirport.city,
        country: destAirport.country
      },
      duration: flightDurationMinutes
    });

    totalDurationMinutes += flightDurationMinutes;
    totalPrice += Number(flight.price);

    // Add layover information if not the last segment
    if (i < flightSegments.length - 1) {
      const nextFlight = flightSegments[i + 1];
      const nextDepartLocal = moment.tz(
        nextFlight.departureTime,
        'YYYY-MM-DDTHH:mm:ss',
        airportMap[nextFlight.origin].timezone
      );
      const nextDepartUTC = nextDepartLocal.utc();

      const layoverMinutes = nextDepartUTC.diff(arriveUTC, 'minutes');

      segments[i].layover = {
        airport: flight.destination,
        duration: layoverMinutes,
        durationFormatted: formatDuration(layoverMinutes)
      };

      totalDurationMinutes += layoverMinutes;
    }
  }

  return {
    segments,
    totalDuration: totalDurationMinutes,
    totalDurationFormatted: formatDuration(totalDurationMinutes),
    totalPrice: totalPrice.toFixed(2),
    stops: flightSegments.length - 1
  };
}

module.exports = {
  searchFlights
};
