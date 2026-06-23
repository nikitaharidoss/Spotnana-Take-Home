# SkyPath: Flight Connection Search Engine

### Running the Application

```bash
git clone https://github.com/nikitaharidoss/Spotnana-Take-Home.git
cd Spotnana-Take-Home
docker-compose up
```

Then open your browser to **http://localhost:3000**

## 📁 Project Structure

```
.
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── main.py            # FastAPI application & endpoints
│   │   ├── flight_search.py   # Core search algorithm
│   │   ├── validation.py      # Input validation
│   │   └── utils.py           # Timezone & utility functions
│   ├── tests/                 # Unit tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.js            # Main application component
│   │   ├── SearchForm.js     # Search input component
│   │   ├── Results.js        # Results display component
│   │   ├── App.css           # Styling
│   │   └── *.test.js         # Unit tests
│   ├── package.json          # Node dependencies
│   └── Dockerfile            # Frontend container
├── flights.json              # Flight dataset (~260 flights, 25 airports)
├── docker-compose.yml        # Container orchestration
└── README.md                 # This file
```

## 🏗️ Architecture

### Backend (Python + FastAPI)

**Tech Stack:** FastAPI, Uvicorn, Pytest

**Key Components:**
- **`main.py`** - Starts backend service and defines REST APIs
- **`flight_search.py`** - Defines functions for flight search
- **`validation.py`** - Validates connections, airport codes, date format, etc.
- **`utils.py`** - Defines utility functions for timezone conversions

**API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/airports` - List all airports with metadata
- `POST /api/search` - Search for flight itineraries
  - Request: `{ origin, destination, date }`
  - Response: List of valid itineraries sorted by travel time with segments, layover info, and pricing

### Frontend (React + Axios)

**Tech Stack:** React 18, Axios, CSS3

**Features:**
- Search form with autocomplete airport suggestions
- Date picker for departure date
- Results display with layover details
- Loading and error states
- Dynamic background that rotates through popular destinations

## 🔍 Search Algorithm

The flight search uses a **Depth-First Search (DFS)** approach with pruning to find all valid routes:

1. **Start from origin** with all flights departing on the requested date
2. **Recursively explore** each path depth-first, up to MAX_STOPS (2)
3. **Validate connections** between each pair of flights using connection rules
4. **Prune branches** that exceed max stops or revisit airports
5. **Collect valid itineraries** when destination is reached
6. **Sort by total travel time** (shortest first)

### Connection Rules Implemented

| Rule | Requirement | Implementation |
|------|-------------|-----------------|
| **Minimum layover (domestic)** | 45 minutes | Checked in `utils.py` |
| **Minimum layover (international)** | 90 minutes | Country comparison via airport data |
| **Maximum layover** | 6 hours | Enforced during connection validation |
| **Same airport constraint** | No airport changes during layover | Destination airport must equal next origin |
| **Timezone-aware calculations** | All times local airport time | Use Python datetime and ZoneInfo modules to calculate duration |

**Domestic vs International:**
- Domestic: Both connecting flights within the same country
- International: At least one flight crosses country borders
- Determined via `airport['country']` field in dataset

## ⚙️ Technical Decisions & Rationale

### 1. **DFS Algorithm for Flight Search**
- **Why:** Natural fit for exploring all paths up to a fixed depth (MAX_STOPS = 2)
- **Implementation:** Recursive DFS with pruning using adjacency list 
- **Efficiency:** Best case: O(A + P), number of airports + number of flight paths; pruning limits depth of search as well
- **Tradeoff:** Could speed up with pre-computed connections, but this is fine for a small data set

### 2. **FastAPI + Uvicorn Backend**
- **Why:** Async-capable, minimal overhead
- **CORS enabled:** Frontend and backend run in separate containers
- **Tradeoff:** FastAPI is better for validation of API requests, although other frameworks like Flask are more lightweight

### 3. **React Frontend**
- **Why:** Component-based architecture scales well; familiar ecosystem
- **State management:** Simple `useState` for MVP; could use Redux for complexity
- **Tradeoff:** Lightweight vs full-featured frameworks, but light weight is fine for this use case

### 4. **Python datetime and ZoneInfo for Timezone Handling**
- **Why:** Need to handle timezone conversions to calculate duration properly
- **Implementation:** All duration calculations done in UTC internally, displayed in local time
- **Tradeoff:** Need to download tzdata if running on system that doesn't have time zone info natively. Running in alpine docker container, so fine for this case

## 🧪 Testing

### Backend Tests
```bash
cd backend && python3 -m pytest -q
```
### Frontend Tests
```bash
cd frontend && npm install && npm test -- --watchAll=false && npm run build
```

Test coverage includes:
- Search form input handling
- Results display rendering
- Error state handling
- Loading state UI

## 📊 Test Cases Verified

All six challenge test cases pass:

| Test | Scenario | Status |
|------|----------|--------|
| 1 | JFK → LAX (direct + connections) | ✅ Returns direct and multi-stop |
| 2 | SFO → NRT (international, 90-min layover) | ✅ Enforces international rules |
| 3 | BOS → SEA (no direct, requires connections) | ✅ Finds valid multi-stop |
| 4 | JFK → JFK (same airport) | ✅ Returns empty/validation error |
| 5 | XXX → LAX (invalid code) | ✅ Graceful error handling |
| 6 | SYD → LAX (date line crossing) | ✅ Correct timezone arithmetic |

## 🚧 Future Improvements

- **Passenger preferences** - Filter by price range, airline, departure time
- **Return flights** - Round-trip search capability
- **Support for real-time data** - Keep track of currently available flights, validate flight isn't sold out
- **Ability to book flights** - Right now this is just a flight search engine, would be nice to be able to book as well
- **User Accounts** - So users can save searches, keep track of bookings, etc.
---
