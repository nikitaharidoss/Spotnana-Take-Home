import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import SearchForm from './SearchForm';

const airports = [
  { code: 'JFK', name: 'John F. Kennedy International', city: 'New York' },
  { code: 'LAX', name: 'Los Angeles International', city: 'Los Angeles' },
];

test('shows suggestions and submits normalized params', async () => {
  const user = userEvent.setup();
  const onSearch = jest.fn();

  render(<SearchForm onSearch={onSearch} airports={airports} />);

  await user.type(screen.getByLabelText(/from/i), 'jf');
  await user.click(screen.getByText(/JFK/i));
  await user.type(screen.getByLabelText(/to/i), 'lax');
  await user.clear(screen.getByLabelText(/date/i));
  await user.type(screen.getByLabelText(/date/i), '2024-03-15');
  await user.click(screen.getByRole('button', { name: /search flights/i }));

  expect(onSearch).toHaveBeenCalledTimes(1);
  expect(onSearch).toHaveBeenCalledWith({
    origin: 'JFK',
    destination: 'LAX',
    date: '2024-03-15',
  });
});
