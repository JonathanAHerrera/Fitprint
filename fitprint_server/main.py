from fastapi import FastAPI, HTTPException
from database import dynamodb_service
from api.models import ItemCreate, ItemUpdate, ItemKey
from api.routes.clothing_routes import router as clothing_router
from api.routes.sustainability_routes import router as sustainability_router

app = FastAPI(title="Fitprint API", description="API for Fitprint fitness tracking app")

# Include routes
app.include_router(clothing_router)
app.include_router(sustainability_router)

@app.get("/")
async def root():
    return {"message": "Hello World", "api": "Fitprint API"}

# DynamoDB CRUD endpoints
@app.post("/items")
async def create_item(item: ItemCreate):
    """Create a new item in DynamoDB"""
    result = await dynamodb_service.create_item(item.data)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.get("/items/{clothing_id}")
async def get_item(clothing_id: str, brand: str = None):
    """Get an item by clothing_id and brand"""
    key = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.get_item(key)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["error"])

@app.put("/items/{clothing_id}")
async def update_item(clothing_id: str, update_data: ItemUpdate, brand: str = None):
    """Update an item"""
    key = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.update_item(
        key, 
        update_data.update_expression, 
        update_data.expression_attribute_values
    )
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.delete("/items/{clothing_id}")
async def delete_item(clothing_id: str, brand: str = None):
    """Delete an item"""
    key = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.delete_item(key)
    if result["success"]:
        return {"message": "Item deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.get("/items")
async def list_items(limit: int = 100):
    """List all items in the table"""
    result = await dynamodb_service.scan_table(limit)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Fitprint API"}
