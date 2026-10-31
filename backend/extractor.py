import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()

class FarmerProfileSchema(BaseModel):
    state: Optional[str] = Field(default=None, description="State name")
    district: Optional[str] = Field(default=None, description="District name")
    caste_category: Optional[str] = Field(default=None, description="Caste category (e.g., SC, ST, OBC, General)")
    land_holding_ha: Optional[float] = Field(default=None, description="Land holding in hectares")
    farmer_type: Optional[str] = Field(default=None, description="Small, Marginal, Large, etc.")
    annual_income: Optional[float] = Field(default=None, description="Annual income in INR")
    gender: Optional[str] = Field(default=None, description="Gender of the applicant")
    age: Optional[int] = Field(default=None, description="Age of the applicant")
    is_taxpayer: Optional[bool] = Field(default=None, description="Taxpayer status")
    occupation_type: Optional[str] = Field(default=None, description="Primary occupation")

PROMPT = """You are an expert government scheme eligibility parser...
Parse the farmer details strictly into the target structured schema. Set null for unspecified fields."""

def extract(text: str, model_name: Optional[str] = None) -> dict:
    selected_model = model_name if model_name else MODEL
    
    response = client.models.generate_content(
        model=selected_model,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT,
            response_mime_type="application/json",
            response_schema=FarmerProfileSchema,
            temperature=0.0,
        ),
    )
    
    return json.loads(response.text)