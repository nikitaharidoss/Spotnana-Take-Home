import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import App from './App';

const airportsPayload = [
  { code: 'JFK', name: 'John F. Kennedy International', city: 'New York' },
  { code: 'LAX', name: 'Los Angeles International', city: 'Los Angeles' },
];

beforeEach(() => {
  jest.spyOn(global, 'fetch');
});

afterEach(() => {
  jest.restoreAllMocks();
});

test('shows API validation errors from search', async () => {
  const user = userEvent.setup();

  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => airportsPayload,
    })
    .mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        details: ['ERROR: Origin and destination cannot be the same.'],
      }),
    });

  render(<App />);

  await user.type(screen.getByLabelText(/from/i), 'JFK');
  await user.type(screen.getByLabelText(/to/i), 'JFK');
  await user.click(screen.getByRole('button', { name: /search flights/i }));

  expect(await screen.findByText(/Origin and destination cannot be the same/i)).toBeInTheDocument();
});

test('renders results on successful search response', async () => {
  const user = userEvent.setup();

  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => airportsPayload,
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        itineraries: [
          {
            totalDurationFormatted: '5h',
            totalPrice: '300.00',
            stops: 0,
            segments: [
              {
                flightNumber: 'SP100',
                airline: 'SkyPath Airways',
                aircraft: 'A320',
                duration: 300,
                departure: {
                  airport: 'JFK',
                  airportName: 'John F. Kennedy International',
                  city: 'New York',
                  time: '08:00',
                  isoTime: '2024-03-15T08:00:00',
                },
                arrival: {
                  airport: 'LAX',
                  airportName: 'Los Angeles International',
                  city: 'Los Angeles',
                  time: '11:00',
                  isoTime: '2024-03-15T11:00:00',
                },
              },
            ],
          },
        ],
      }),
    });

  render(<App />);

  await user.type(screen.getByLabelText(/from/i), 'JFK');
  await user.type(screen.getByLabelText(/to/i), 'LAX');
  await user.click(screen.getByRole('button', { name: /search flights/i }));

  await waitFor(() => {
    expect(screen.queryByText(/Searching flights/i)).not.toBeInTheDocument();
  });
  expect(await screen.findByText(/Available Flights/i)).toBeInTheDocument();
  expect(screen.getByText(/\$300.00/i)).toBeInTheDocument();
});
