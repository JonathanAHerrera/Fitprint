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
    clothing_id: str
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
