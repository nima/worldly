from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from fuzzywuzzy import process  # For fuzzy matching

from worldly.play import quiz_bank

# Initialize Quiz Object
q = quiz_bank()  # Initialize FastAPI
microservice = FastAPI()


# Fuzzy Matching Function
def find_matching_countries(df: pd.DataFrame, country_name: str) -> List[str]:
    """Find matching countries in a dimension using fuzzy matching."""
    matches = []
    for _, row in df.iterrows():
        all_countries = (
            [c for sublist in row["countries"] for c in sublist] if isinstance(row["countries"], list) else []
        )
        match, score = process.extractOne(country_name, all_countries)
        if score >= 80:
            matches.append(match)
    return matches


# Pydantic Model for API Response
class DimensionResponse(BaseModel):
    dimension: str
    matches: List[str]


# Endpoint: List All Dimensions
@microservice.get("/dimensions", response_model=List[str])
def list_dimensions():
    """List all available dimensions."""
    return list(q.dimensions)


# Endpoint: Find Matching Dimensions for a Country
@microservice.get("/dimensions/matches", response_model=List[DimensionResponse])
def get_matching_dimensions(country_name: str):
    """
    Return dimensions where a given country name appears, using fuzzy matching.
    """
    results = []
    for dimension in q.dimensions:
        df = getattr(q, dimension, None)
        if df is not None and "countries" in df.columns:
            matches = find_matching_countries(df, country_name)
            if matches:
                results.append(DimensionResponse(dimension=dimension, matches=matches))
    if not results:
        raise HTTPException(status_code=404, detail="No matches found for the given country name.")
    return results
