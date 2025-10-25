from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
from database import dynamodb_service
from ..models import SustainabilityReportCreate, SustainabilityReport

# Create router for sustainability report endpoints
router = APIRouter(prefix="/sustainability", tags=["sustainability"])

@router.post("/reports")
async def create_sustainability_report(report: SustainabilityReportCreate):
    """Create a new sustainability report"""
    # Generate a unique report ID
    report_id = f"rep_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:3]}"
    
    item_data = {
        "clothing_id": report.clothing_id,
        "report_id": report_id,
        "brand": report.brand,
        "categories": report.categories.dict(),
        "overall_score": report.overall_score,
        "overall_description": report.overall_description,
        "regional_alerts": report.regional_alerts.dict(),
        "alternative_ids": report.alternative_ids,
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    # Convert to DynamoDB format
    import json
    item_data = json.loads(json.dumps(item_data))
    
    result = await dynamodb_service.create_item(item_data, table_name="sustainability")
    if result["success"]:
        return {
            "message": "Sustainability report created successfully",
            "report_id": report_id,
            "item": result["item"]
        }
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@router.get("/reports/{report_id}")
async def get_sustainability_report(report_id: str):
    """Get a sustainability report by ID"""
    key = {"report_id": report_id}
    result = await dynamodb_service.get_item(key, table_name="sustainability")
    if result["success"]:
        return result["item"]
    else:
        raise HTTPException(status_code=404, detail=result["error"])

@router.get("/reports/clothing/{clothing_id}")
async def get_clothing_sustainability_report(clothing_id: str):
    """Get sustainability report for a specific clothing item"""
    # Query by clothing_id - in production you'd want a GSI
    result = await dynamodb_service.scan_table(1000, table_name="sustainability")
    if result["success"]:
        clothing_reports = [item for item in result["items"] if item.get("clothing_id") == clothing_id]
        if clothing_reports:
            return {"reports": clothing_reports, "count": len(clothing_reports)}
        else:
            raise HTTPException(status_code=404, detail="No sustainability report found for this clothing item")
    else:
        raise HTTPException(status_code=500, detail=result["error"])

@router.get("/reports")
async def list_sustainability_reports(limit: int = 100):
    """List all sustainability reports"""
    result = await dynamodb_service.scan_table(limit, table_name="sustainability")
    if result["success"]:
        return {"reports": result["items"], "count": len(result["items"])}
    else:
        raise HTTPException(status_code=500, detail=result["error"])

@router.delete("/reports/{report_id}")
async def delete_sustainability_report(report_id: str):
    """Delete a sustainability report"""
    key = {"report_id": report_id}
    result = await dynamodb_service.delete_item(key, table_name="sustainability")
    if result["success"]:
        return {"message": "Sustainability report deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@router.get("/scores/summary")
async def get_sustainability_summary():
    """Get summary statistics of sustainability scores"""
    result = await dynamodb_service.scan_table(1000, table_name="sustainability")
    if result["success"]:
        reports = result["items"]
        if not reports:
            return {"message": "No sustainability reports found"}
        
        scores = [report.get("overall_score", 0) for report in reports if report.get("overall_score")]
        if scores:
            return {
                "total_reports": len(reports),
                "average_score": round(sum(scores) / len(scores), 2),
                "highest_score": max(scores),
                "lowest_score": min(scores),
                "score_distribution": {
                    "excellent": len([s for s in scores if s >= 4.0]),
                    "good": len([s for s in scores if 3.0 <= s < 4.0]),
                    "fair": len([s for s in scores if 2.0 <= s < 3.0]),
                    "poor": len([s for s in scores if s < 2.0])
                }
            }
        else:
            return {"message": "No valid scores found in reports"}
    else:
        raise HTTPException(status_code=500, detail=result["error"])
