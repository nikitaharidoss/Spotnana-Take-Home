const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { searchFlights } = require('./flightSearch');
const { validateSearchInput, airportExists } = require('./validation');

const app = express();
app.use(cors());
app.use(express.json());

// Load flights data
const flightsData = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../flights.json'), 'utf-8')
);

const { flights, airports } = flightsData;

// Build airport map for quick lookup
const airportMap = {};
airports.forEach((airport) => {
  airportMap[airport.code] = airport;
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Get available airports
app.get('/api/airports', (req, res) => {
  res.json(airports);
});

// Search endpoint
app.post('/api/search', (req, res) => {
  const { origin, destination, date } = req.body;

  // Validate inputs
  const validation = validateSearchInput(origin?.toUpperCase(), destination?.toUpperCase(), date);
  if (!validation.valid) {
    return res.status(400).json({
      error: 'Invalid search parameters',
      details: validation.errors
    });
  }

  const originCode = origin.toUpperCase();
  const destCode = destination.toUpperCase();

  // Check airports exist
  if (!airportExists(originCode, airportMap)) {
    return res.status(400).json({
      error: 'Invalid airport code',
      details: [`Airport ${originCode} not found`]
    });
  }

  if (!airportExists(destCode, airportMap)) {
    return res.status(400).json({
      error: 'Invalid airport code',
      details: [`Airport ${destCode} not found`]
    });
  }

  try {
    const itineraries = searchFlights(originCode, destCode, date, flights, airports);

    res.json({
      search: {
        origin: originCode,
        destination: destCode,
        date
      },
      results: itineraries,
      count: itineraries.length
    });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      error: 'Internal server error',
      details: [error.message]
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    error: 'Internal server error',
    details: [err.message]
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`SkyPath backend running on http://localhost:${PORT}`);
  console.log(`Loaded ${flights.length} flights across ${airports.length} airports`);
});
