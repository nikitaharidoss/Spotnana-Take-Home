import React, { useState, useEffect } from 'react';
import './App.css';
import SearchForm from './SearchForm';
import Results from './Results';

const destinationBackgrounds = [
  {
    name: 'Paris',
    image: 'https://images.unsplash.com/photo-1431274172761-fca41d930114?auto=format&fit=crop&w=1600&q=80'
  },
  {
    name: 'Tokyo',
    image: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1600&q=80'
  },
  {
    name: 'New York',
    image: 'https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?auto=format&fit=crop&w=1600&q=80'
  },
  {
    name: 'Sydney',
    image: 'https://images.unsplash.com/photo-1523428096881-5bd79d043006?auto=format&fit=crop&w=1600&q=80'
  },
  {
    name: 'Dubai',
    image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1600&q=80'
  }
];

function App() {
  const [searchParams, setSearchParams] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [airports, setAirports] = useState([]);
  const [activeBackgroundIndex, setActiveBackgroundIndex] = useState(0);

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

  useEffect(() => {
    const intervalId = setInterval(() => {
      setActiveBackgroundIndex(
        (currentIndex) => (currentIndex + 1) % destinationBackgrounds.length
      );
    }, 8000);

    return () => clearInterval(intervalId);
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
        // setResults([]);
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
      <div className="background-rotator" aria-hidden="true">
        {destinationBackgrounds.map((background, index) => (
          <div
            key={background.name}
            className={`bg-slide ${index === activeBackgroundIndex ? 'active' : ''}`}
            style={{ backgroundImage: `url(${background.image})` }}
          />
        ))}
      </div>

      <div className="app-content">
        <header className="header">
          <h1>SkyPath</h1>
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
          <p>© 2024 SkyPath Airways. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
