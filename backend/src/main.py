import json
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from flight_search import FlightSearcher
from validation import validate_search_input, airport_exists

# Load flights data
flights_path = os.path.join(os.path.dirname(__file__), '..', 'flights.json')
with open(flights_path, 'r') as f:
    data = json.load(f)

flights = data['flights']
airports = data['airports']

# Create airport map
airport_map = {airport['code']: airport for airport in airports}

searcher = FlightSearcher(flights, airports)

# Create FastAPI app
app = FastAPI(title="SkyPath Flight Search API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    origin: str
    destination: str
    date: str

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/api/airports")
def get_airports():
    """Get list of available airports"""
    return airports

@app.post("/api/search")
def search(request: SearchRequest):
    """Search for flights"""
    origin = request.origin.upper()
    destination = request.destination.upper()
    date = request.date
    
    # Validate inputs
    validation = validate_search_input(origin, destination, date)
    if not validation['valid']:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid search parameters",
                "details": validation['errors']
            }
        )
    
    # Check airports exist
    if not airport_exists(origin, airport_map):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid airport code",
                "details": [f"Airport {origin} not found"]
            }
        )
    
    if not airport_exists(destination, airport_map):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid airport code",
                "details": [f"Airport {destination} not found"]
            }
        )
    
    try:
        itineraries = searcher.search(origin, destination, date)
        
        return {
            "search": {
                "origin": origin,
                "destination": destination,
                "date": date
            },
            "itineraries": itineraries,
            "count": len(itineraries)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "details": [str(e)]
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "5001"))
    print(f"SkyPath backend running on http://localhost:{port}")
    print(f"Loaded {len(flights)} flights across {len(airports)} airports")
    uvicorn.run(app, host="0.0.0.0", port=port)
