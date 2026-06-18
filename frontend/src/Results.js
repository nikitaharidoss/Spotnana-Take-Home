import React from 'react';

function Results({ searchParams, itineraries, airports }) {
  if (itineraries.length === 0) {
    return (
      <div className="results">
        <div className="empty-state">
          <h2>No flights found</h2>
          <p>
            No direct or connecting flights available from {searchParams.origin} to{' '}
            {searchParams.destination} on {searchParams.date}. Try different dates or airports.
          </p>
        </div>
      </div>
    );
  }

  const airportMap = {};
  airports.forEach((a) => {
    airportMap[a.code] = a;
  });

  return (
    <div className="results">
      <div className="results-header">
        <h2>Available Flights</h2>
        <p className="result-count">
          Found {itineraries.length} itinerary{itineraries.length !== 1 ? 'ies' : ''} (sorted by
          shortest travel time)
        </p>
      </div>

      <div className="itineraries-list">
        {itineraries.map((itinerary, index) => (
          <div key={index} className="itinerary-card">
            <div className="itinerary-summary">
              <div className="route">
                <span className="airport-code">{itinerary.segments[0].departure.airport}</span>
                <span className="separator">→</span>
                <span className="airport-code">
                  {itinerary.segments[itinerary.segments.length - 1].arrival.airport}
                </span>
                {itinerary.stops > 0 && (
                  <span className="stops-badge">
                    {itinerary.stops} stop{itinerary.stops !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
              <div className="duration-price">
                <span className="duration">⏱️ {itinerary.totalDurationFormatted}</span>
                <span className="price">${itinerary.totalPrice}</span>
              </div>
            </div>

            <div className="itinerary-details">
              {itinerary.segments.map((segment, segIdx) => (
                <div key={segIdx}>
                  <div className="flight-segment">
                    <div className="segment-times">
                      <div className="time-block">
                        <div className="time">{segment.departure.time}</div>
                        <div className="airport-info">
                          <div className="airport-code">{segment.departure.airport}</div>
                          <div className="airport-name">{segment.departure.airportName}</div>
                          <div className="city">{segment.departure.city}</div>
                        </div>
                      </div>

                      <div className="flight-info">
                        <div className="duration">{Math.floor(segment.duration / 60)}h {segment.duration % 60}m</div>
                        <div className="flight-number">{segment.flightNumber}</div>
                        <div className="airline">{segment.airline}</div>
                        <div className="aircraft">{segment.aircraft}</div>
                      </div>

                      <div className="time-block">
                        <div className="time">{segment.arrival.time}</div>
                        <div className="airport-info">
                          <div className="airport-code">{segment.arrival.airport}</div>
                          <div className="airport-name">{segment.arrival.airportName}</div>
                          <div className="city">{segment.arrival.city}</div>
                        </div>
                      </div>
                    </div>

                    {segment.layover && (
                      <div className="layover">
                        <span className="layover-label">
                          ⏸️ Layover in {segment.layover.airport}: {segment.layover.durationFormatted}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Results;
