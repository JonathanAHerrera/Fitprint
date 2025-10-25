from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import dynamodb_service
from ..models import ClothingCreate, ClothingUpdate

# Create router for clothing endpoints
router = APIRouter(prefix="/clothing", tags=["clothing"])

@router.post("/")
async def create_clothing_item(clothing: ClothingCreate):
    """Create a new clothing item"""
    item_data = {
        "clothing_id": clothing.clothing_id,
        "brand": clothing.brand,
        "image_file": clothing.image_file,
        "created_at": str(datetime.now().isoformat())
    }
    result = await dynamodb_service.create_item(item_data)
    if result["success"]:
        return {"message": "Clothing item created successfully", "item": result["item"]}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@router.get("/{clothing_id}")
async def get_clothing_item(clothing_id: str, brand: str = None):
    """Get a clothing item by ID and brand"""
    key = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.get_item(key)
    if result["success"]:
        return result["item"]
    else:
        raise HTTPException(status_code=404, detail=result["error"])

@router.put("/{clothing_id}")
async def update_clothing_item(clothing_id: str, brand: str, update_data: ClothingUpdate):
    """Update a clothing item"""
    key = {"clothing_id": clothing_id, "brand": brand}
    
    # Build update expression dynamically
    update_expression = "SET "
    expression_values = {}
    
    if update_data.brand is not None:
        update_expression += "brand = :brand, "
        expression_values[":brand"] = update_data.brand
    
    if update_data.image_file is not None:
        update_expression += "image_file = :image_file, "
        expression_values[":image_file"] = update_data.image_file
    
    # Add updated timestamp
    update_expression += "updated_at = :updated_at"
    expression_values[":updated_at"] = str(datetime.now().isoformat())
    
    result = await dynamodb_service.update_item(key, update_expression, expression_values)
    if result["success"]:
        return {"message": "Clothing item updated successfully", "response": result["response"]}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@router.delete("/{clothing_id}")
async def delete_clothing_item(clothing_id: str, brand: str):
    """Delete a clothing item"""
    key = {"clothing_id": clothing_id, "brand": brand}
    result = await dynamodb_service.delete_item(key)
    if result["success"]:
        return {"message": "Clothing item deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@router.get("/")
async def list_clothing_items(limit: int = 100):
    """List all clothing items"""
    result = await dynamodb_service.scan_table(limit)
    if result["success"]:
        return {"items": result["items"], "count": len(result["items"])}
    else:
        raise HTTPException(status_code=500, detail=result["error"])
