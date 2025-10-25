from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from datetime import datetime
import uuid
import logging
from database import dynamodb_service
from services.s3_service import s3_service
from services.google_search_service import google_search_service
from services.gemini_service import gemini_service
from services.fast_gemini_service import fast_gemini_service
from ..models import (
    OutfitAnalysisResponse, 
    ClothingResponse, 
    SustainabilityReport,
    AlternativeProduct,
    ImageUploadResponse
)

logger = logging.getLogger(__name__)

# Create router for analysis endpoints
router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/outfit", response_model=OutfitAnalysisResponse)
async def analyze_outfit(
    user_id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Analyze an outfit image and generate sustainability report with alternatives.
    
    This endpoint:
    1. Uploads the image to S3
    2. Performs Google reverse image search
    3. Generates sustainability report via Gemini AI
    4. Finds 3 sustainable alternatives via Gemini AI
    5. Stores all data in DynamoDB
    """
    analysis_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat() + "Z"
    
    try:
        # Step 1: Upload image to S3
        logger.info(f"Starting outfit analysis for user {user_id}")
        
        image_content = await image.read()
        upload_result = await s3_service.upload_image(
            file_content=image_content,
            user_id=user_id,
            original_filename=image.filename
        )
        
        if not upload_result["success"]:
            raise HTTPException(status_code=400, detail=f"Image upload failed: {upload_result['error']}")
        
        image_url = upload_result["image_url"]
        logger.info(f"Image uploaded successfully: {image_url}")
        
        # Step 2: Use Gemini Vision to identify the brand from the image
        logger.info("Using Gemini Vision to identify brand from image...")
        vision_result = await fast_gemini_service.identify_brand_from_image(image_url)
        
        if vision_result["success"]:
            brand_info = vision_result["brand_info"]
            logger.info(f"Brand identified by Gemini Vision: {brand_info['brand']} (confidence: {brand_info.get('confidence', 0)})")
        else:
            logger.warning(f"Gemini Vision failed: {vision_result.get('error', 'Unknown error')}")
            brand_info = vision_result["brand_info"]  # Use fallback data
        
        logger.info(f"Brand identified: {brand_info['brand']}")
        
        # Step 3: Generate sustainability report via Fast Gemini
        logger.info("Generating sustainability report...")
        report_result = await fast_gemini_service.generate_sustainability_report(
            brand=brand_info["brand"],
            product_info=brand_info
        )
        
        if not report_result["success"]:
            logger.warning(f"Gemini report generation failed: {report_result['error']}")
            # Use fallback report
            report_data = gemini_service._create_fallback_report()
        else:
            report_data = report_result["report_data"]
        
        # Step 4: Generate search query and find sustainable alternatives via Google Shopping
        logger.info("Generating shopping search query...")
        search_query = await fast_gemini_service.generate_shopping_search_query(
            brand=brand_info["brand"],
            product_info=brand_info
        )
        
        logger.info(f"Searching Google Shopping with query: {search_query}")
        shopping_result = await google_search_service.search_shopping_results(
            query=search_query,
            num_results=3
        )
        
        if not shopping_result["success"] or len(shopping_result["alternatives"]) == 0:
            logger.warning(f"Google Shopping search failed or returned no results: {shopping_result.get('error', 'No results')}")
            # Use fallback alternatives
            alternatives_data = [
                {
                    "name": "Organic Cotton T-Shirt",
                    "brand": "Patagonia",
                    "image_url": "",
                    "sustainability_score": 4.5,
                    "link": "https://www.patagonia.com",
                    "why_sustainable": "Made with 100% organic cotton and Fair Trade certified"
                },
                {
                    "name": "Recycled Polyester Hoodie", 
                    "brand": "Reformation",
                    "image_url": "",
                    "sustainability_score": 4.2,
                    "link": "https://www.thereformation.com",
                    "why_sustainable": "Uses recycled polyester from plastic bottles, carbon neutral shipping"
                },
                {
                    "name": "Hemp Blend Jeans",
                    "brand": "Everlane", 
                    "image_url": "",
                    "sustainability_score": 4.7,
                    "link": "https://www.everlane.com",
                    "why_sustainable": "Hemp requires 50% less water than cotton, biodegradable materials"
                }
            ]
        else:
            alternatives_data = shopping_result["alternatives"]
            logger.info(f"Found {len(alternatives_data)} alternatives from Google Shopping")
        
        # Step 5: Create clothing item
        clothing_id = str(uuid.uuid4())
        clothing_item = {
            "clothing_id": clothing_id,
            "user_id": user_id,
            "brand": brand_info.get("brand", "Unknown Brand") or "Unknown Brand",
            "image_file": image_url,
            "created_at": created_at
        }
        
        clothing_result = await dynamodb_service.create_item(clothing_item, table_name="clothing")
        if not clothing_result["success"]:
            logger.error(f"Failed to create clothing item: {clothing_result['error']}")
            raise HTTPException(status_code=500, detail="Failed to save clothing item")
        
        # Step 6: Create sustainability report
        report_id = f"rep_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Convert report data to proper format
        categories_data = report_data.get("categories", {})
        regional_alerts_data = report_data.get("regional_alerts", {})
        
        sustainability_report = {
            "report_id": report_id,
            "clothing_id": clothing_id,
            "brand": brand_info.get("brand", "Unknown Brand") or "Unknown Brand",
            "categories": categories_data,
            "overall_score": report_data.get("overall_score", 3.0),
            "overall_description": report_data.get("overall_description", "Sustainability analysis completed"),
            "regional_alerts": regional_alerts_data,
            "alternative_ids": [],  # Will be populated after creating alternatives
            "created_at": created_at
        }
        
        report_result = await dynamodb_service.create_item(sustainability_report, table_name="sustainability")
        if not report_result["success"]:
            logger.error(f"Failed to create sustainability report: {report_result['error']}")
            raise HTTPException(status_code=500, detail="Failed to save sustainability report")
        
        # Step 7: Create alternatives
        alternative_ids = []
        created_alternatives = []
        
        for i, alt_data in enumerate(alternatives_data[:3]):  # Limit to 3 alternatives
            alternative_id = str(uuid.uuid4())
            alternative_ids.append(alternative_id)
            
            alternative_item = {
                "alternative_id": alternative_id,
                "clothing_id": clothing_id,
                "name": alt_data.get("name", f"Alternative {i+1}"),
                "brand": alt_data.get("brand", "Unknown Brand"),
                "image_url": alt_data.get("image_url", ""),
                "sustainability_score": alt_data.get("sustainability_score", 4.0),
                "link": alt_data.get("link", ""),
                "why_sustainable": alt_data.get("why_sustainable", "Sustainable alternative"),
                "created_at": created_at
            }
            
            alt_result = await dynamodb_service.create_item(alternative_item, table_name="alternatives")
            if alt_result["success"]:
                created_alternatives.append(AlternativeProduct(**alternative_item))
            else:
                logger.warning(f"Failed to create alternative {i+1}: {alt_result['error']}")
        
        # Update sustainability report with alternative IDs
        if alternative_ids:
            update_result = await dynamodb_service.update_item(
                key={"report_id": report_id},
                update_expression="SET alternative_ids = :alt_ids",
                expression_attribute_values={":alt_ids": alternative_ids},
                table_name="sustainability"
            )
            if not update_result["success"]:
                logger.warning(f"Failed to update report with alternative IDs: {update_result['error']}")
        
        # Prepare response
        response = OutfitAnalysisResponse(
            clothing_item=ClothingResponse(
                clothing_id=clothing_id,
                user_id=user_id,
                brand=brand_info.get("brand", "Unknown Brand") or "Unknown Brand",
                image_file=image_url,
                created_at=created_at
            ),
            sustainability_report=SustainabilityReport(
                clothing_id=clothing_id,
                report_id=report_id,
                brand=brand_info.get("brand", "Unknown Brand") or "Unknown Brand",
                categories=categories_data,
                overall_score=report_data.get("overall_score", 3.0),
                overall_description=report_data.get("overall_description", "Sustainability analysis completed"),
                regional_alerts=regional_alerts_data,
                alternative_ids=alternative_ids,
                created_at=created_at
            ),
            alternatives=created_alternatives,
            analysis_id=analysis_id,
            created_at=created_at
        )
        
        logger.info(f"Outfit analysis completed successfully for user {user_id}")
        logger.info(f"Sending {len(created_alternatives)} alternatives to frontend")
        for i, alt in enumerate(created_alternatives):
            logger.info(f"Alternative {i+1}: {alt.name} | image_url: {alt.image_url} | link: {alt.link}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Outfit analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/outfit/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by analysis ID"""
    # This would require storing analysis_id in a separate table or adding it to existing tables
    # For now, return a placeholder
    return {"message": "Analysis retrieval not yet implemented", "analysis_id": analysis_id}

@router.get("/outfit/user/{user_id}")
async def get_user_analyses(user_id: str, limit: int = 10):
    """Get all analyses for a specific user"""
    try:
        # Get clothing items for user
        clothing_result = await dynamodb_service.scan_table(limit=100, table_name="clothing")
        if not clothing_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to retrieve clothing items")
        
        user_clothing = [item for item in clothing_result["items"] if item.get("user_id") == user_id]
        
        # Get sustainability reports for these clothing items
        clothing_ids = [item["clothing_id"] for item in user_clothing]
        
        sustainability_result = await dynamodb_service.scan_table(limit=100, table_name="sustainability")
        if not sustainability_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to retrieve sustainability reports")
        
        user_reports = [report for report in sustainability_result["items"] if report.get("clothing_id") in clothing_ids]
        
        return {
            "user_id": user_id,
            "clothing_items": user_clothing,
            "sustainability_reports": user_reports,
            "total_analyses": len(user_reports)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analyses: {str(e)}")
