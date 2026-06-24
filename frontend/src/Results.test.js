import { render, screen } from '@testing-library/react';

import Results from './Results';

const airports = [
  { code: 'JFK', name: 'John F. Kennedy International', city: 'New York' },
  { code: 'LAX', name: 'Los Angeles International', city: 'Los Angeles' },
];

test('renders empty state when no itineraries exist', () => {
  render(
    <Results
      searchParams={{ origin: 'JFK', destination: 'LAX', date: '2024-03-15' }}
      itineraries={[]}
      airports={airports}
    />
  );

  expect(screen.getByText(/No flights found/i)).toBeInTheDocument();
});

test('renders itinerary details including layover label', () => {
  const itineraries = [
    {
      totalDurationFormatted: '7h',
      totalPrice: '250.00',
      stops: 1,
      segments: [
        {
          flightNumber: 'SP100',
          airline: 'SkyPath Airways',
          aircraft: 'A320',
          duration: 120,
          departure: {
            airport: 'JFK',
            airportName: 'John F. Kennedy International',
            city: 'New York',
            time: '08:00',
            isoTime: '2024-03-15T08:00:00',
          },
          arrival: {
            airport: 'ORD',
            airportName: "Chicago O'Hare",
            city: 'Chicago',
            time: '10:00',
            isoTime: '2024-03-15T10:00:00',
          },
          layover: {
            airport: 'ORD',
            durationFormatted: '1h',
          },
        },
        {
          flightNumber: 'SP101',
          airline: 'SkyPath Airways',
          aircraft: 'A320',
          duration: 180,
          departure: {
            airport: 'ORD',
            airportName: "Chicago O'Hare",
            city: 'Chicago',
            time: '11:00',
            isoTime: '2024-03-15T11:00:00',
          },
          arrival: {
            airport: 'LAX',
            airportName: 'Los Angeles International',
            city: 'Los Angeles',
            time: '13:00',
            isoTime: '2024-03-15T13:00:00',
          },
        },
      ],
    },
  ];

  render(
    <Results
      searchParams={{ origin: 'JFK', destination: 'LAX', date: '2024-03-15' }}
      itineraries={itineraries}
      airports={airports}
    />
  );

  expect(screen.getByText(/Available Flights/i)).toBeInTheDocument();
  expect(screen.getByText(/\$250.00/i)).toBeInTheDocument();
  expect(screen.getByText(/Layover in ORD: 1h/i)).toBeInTheDocument();
});
