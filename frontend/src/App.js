import React, { useState, useEffect } from 'react';
import './App.css';
import SearchForm from './SearchForm';
import Results from './Results';

function App() {
  const [searchParams, setSearchParams] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [airports, setAirports] = useState([]);

  // Fetch available airports on mount
  useEffect(() => {
    const fetchAirports = async () => {
      try {
        const response = await fetch('/api/airports');
        const data = await response.json();
        setAirports(data);
      } catch (err) {
        console.error('Failed to load airports:', err);
      }
    };

    fetchAirports();
  }, []);

  const handleSearch = async (params) => {
    setSearchParams(params);
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.details ? errorData.details.join(', ') : 'Search failed');
        setResults([]);
      } else {
        const data = await response.json();
        setResults(Array.isArray(data.itineraries) ? data.itineraries : []);
        setError(null);
      }
    } catch (err) {
      setError('Network error. Please check that the backend server is running.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>✈️ SkyPath</h1>
        <p>Flight Connection Search Engine</p>
      </header>

      <main className="main">
        <SearchForm onSearch={handleSearch} airports={airports} />

        {error && <div className="error-message">{error}</div>}

        {loading && <div className="loading">Searching flights...</div>}

        {results && (
          <Results 
            searchParams={searchParams}
            itineraries={results}
            airports={airports}
          />
        )}
      </main>

      <footer className="footer">
        <p>© 2024 SkyPath Airways. All flights local times.</p>
      </footer>
    </div>
  );
}

export default App;
