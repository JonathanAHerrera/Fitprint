#!/usr/bin/env python3
import asyncio
from database import dynamodb_service

async def test_direct_insert():
    print("🧪 Testing direct DynamoDB insert...")
    
    test_data = {
        "clothing_id": "test123",
        "report_id": "rep_test_001",
        "brand": "Test Brand",
        "categories": {
            "material_origin": {"score": 3, "description": "test"},
            "production_impact": {"score": 3, "description": "test"},
            "labor_ethics": {"score": 3, "description": "test"},
            "end_of_life": {"score": 3, "description": "test"},
            "brand_transparency": {"score": 3, "description": "test"}
        },
        "overall_score": 3.0,
        "overall_description": "Test description",
        "regional_alerts": {},
        "alternative_ids": [],
        "created_at": "2025-10-25T12:00:00Z"
    }
    
    try:
        result = await dynamodb_service.create_item(test_data, table_name="sustainability")
        if result["success"]:
            print("✅ Successfully created sustainability report!")
            print(f"📋 Result: {result}")
        else:
            print(f"❌ Failed to create report: {result['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_insert())
