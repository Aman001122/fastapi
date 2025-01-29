from fastapi import FastAPI, HTTPException, Depends
import httpx
import base64
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# FatSecret API Credentials (Replace with your actual credentials)
CLIENT_ID = "b68e635058d64e94915b1901778617cc"
CLIENT_SECRET = "4d25b9a83ee946bba7db47808d9edf31"

# FatSecret API URLs
TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
SEARCH_URL = "https://platform.fatsecret.com/rest/server.api"


# Function to get OAuth token
def get_access_token():
    """Fetches an access token from FatSecret API"""

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()  # Fix encoding issue

    data = {
        "grant_type": "client_credentials",
        "scope": "basic"
    }

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = httpx.post(TOKEN_URL, data=data, headers=headers)

    print("OAuth Response:", response.text)  # Debugging print

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to retrieve access token: {response.text}")

    return response.json().get("access_token")


# Pydantic Model for Request Body
class FoodSearchRequest(BaseModel):
    search_expression: str
    page_number: Optional[int] = 1
    max_results: Optional[int] = 10


# API Route to Search for Foods
@app.post("/search-foods")
def search_foods(request: FoodSearchRequest, token: str = Depends(get_access_token)):
    """Search for foods using FatSecret API"""

    params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": request.search_expression,
        "page_number": request.page_number,
        "max_results": request.max_results
    }

    headers = {"Authorization": f"Bearer {token}"}

    response = httpx.get(SEARCH_URL, params=params, headers=headers)

    print("FatSecret API Response:", response.text)  # Debugging print

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to retrieve food data: {response.text}")

    return response.json()
