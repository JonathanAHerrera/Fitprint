from pydantic import BaseModel
from typing import Dict, Any, Optional, List
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
    score: float  # Changed from int to float to support decimal scores like 1.5, 2.5, etc.
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

# Image Upload Models
class ImageUploadResponse(BaseModel):
    success: bool
    image_url: str
    filename: str
    bucket: str

# Alternative Product Models
class AlternativeProduct(BaseModel):
    alternative_id: str
    name: str
    brand: str
    image_url: str
    sustainability_score: float
    link: str
    why_sustainable: str
    clothing_id: str  # Reference to original clothing item

class AlternativeProductCreate(BaseModel):
    name: str
    brand: str
    image_url: str
    sustainability_score: float
    link: str
    why_sustainable: str
    clothing_id: str

# Outfit Analysis Models
class OutfitAnalysisRequest(BaseModel):
    user_id: str
    # Image file will be handled separately in the endpoint

class OutfitAnalysisResponse(BaseModel):
    clothing_item: ClothingResponse
    sustainability_report: SustainabilityReport
    alternatives: List[AlternativeProduct]
    analysis_id: str
    created_at: str
