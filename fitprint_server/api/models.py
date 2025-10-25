from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

# Generic models for general DynamoDB operations
class ItemCreate(BaseModel):
    data: Dict[str, Any]

class ItemUpdate(BaseModel):
    update_expression: str
    expression_attribute_values: Dict[str, Any]

class ItemKey(BaseModel):
    key: Dict[str, Any]

# Clothing-specific models
class ClothingCreate(BaseModel):
    user_id: str
    brand: str
    image_file: str

class ClothingUpdate(BaseModel):
    brand: Optional[str] = None
    image_file: Optional[str] = None

class ClothingResponse(BaseModel):
    clothing_id: str
    brand: str
    image_file: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# Sustainability Report Models
class CategoryScore(BaseModel):
    score: int
    description: str

class Categories(BaseModel):
    material_origin: CategoryScore
    production_impact: CategoryScore
    labor_ethics: CategoryScore
    end_of_life: CategoryScore
    brand_transparency: CategoryScore

class RegionalAlerts(BaseModel):
    EU: Optional[str] = None
    CA: Optional[str] = None
    US: Optional[str] = None
    UK: Optional[str] = None

class SustainabilityReport(BaseModel):
    clothing_id: str
    report_id: str
    brand: str
    categories: Categories
    overall_score: float
    overall_description: str
    regional_alerts: RegionalAlerts
    alternative_ids: list[str]
    created_at: str

class SustainabilityReportCreate(BaseModel):
    clothing_id: str
    brand: str
    categories: Categories
    overall_score: float
    overall_description: str
    regional_alerts: RegionalAlerts
    alternative_ids: list[str]
