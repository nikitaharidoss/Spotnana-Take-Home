import React, { useState } from 'react';

function SearchForm({ onSearch, airports }) {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [date, setDate] = useState('2024-03-15');
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [destSuggestions, setDestSuggestions] = useState([]);

  const airportCodes = airports.map((a) => ({ code: a.code, name: a.name, city: a.city }));

  const handleOriginChange = (value) => {
    setOrigin(value.toUpperCase());
    if (value.length > 0) {
      const filtered = airportCodes.filter(
        (a) =>
          a.code.includes(value.toUpperCase()) ||
          a.city.toUpperCase().includes(value.toUpperCase())
      );
      setOriginSuggestions(filtered.slice(0, 5));
    } else {
      setOriginSuggestions([]);
    }
  };

  const handleDestinationChange = (value) => {
    setDestination(value.toUpperCase());
    if (value.length > 0) {
      const filtered = airportCodes.filter(
        (a) =>
          a.code.includes(value.toUpperCase()) ||
          a.city.toUpperCase().includes(value.toUpperCase())
      );
      setDestSuggestions(filtered.slice(0, 5));
    } else {
      setDestSuggestions([]);
    }
  };

  const selectOrigin = (code) => {
    setOrigin(code);
    setOriginSuggestions([]);
  };

  const selectDestination = (code) => {
    setDestination(code);
    setDestSuggestions([]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({
      origin: origin.toUpperCase(),
      destination: destination.toUpperCase(),
      date
    });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="origin">From</label>
        <div className="autocomplete-wrapper">
          <input
            id="origin"
            type="text"
            placeholder="e.g., JFK or New York"
            value={origin}
            onChange={(e) => handleOriginChange(e.target.value)}
            required
          />
          {originSuggestions.length > 0 && (
            <ul className="suggestions">
              {originSuggestions.map((a) => (
                <li key={a.code} onClick={() => selectOrigin(a.code)}>
                  <strong>{a.code}</strong> - {a.name} ({a.city})
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="destination">To</label>
        <div className="autocomplete-wrapper">
          <input
            id="destination"
            type="text"
            placeholder="e.g., LAX or Los Angeles"
            value={destination}
            onChange={(e) => handleDestinationChange(e.target.value)}
            required
          />
          {destSuggestions.length > 0 && (
            <ul className="suggestions">
              {destSuggestions.map((a) => (
                <li key={a.code} onClick={() => selectDestination(a.code)}>
                  <strong>{a.code}</strong> - {a.name} ({a.city})
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="date">Date</label>
        <input
          id="date"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          min="2024-03-15"
          max="2024-03-16"
          required
        />
      </div>

      <button type="submit" className="btn-search">
        Search Flights
      </button>
    </form>
  );
}

export default SearchForm;
