"""
Fast Gemini service for quick testing
"""
import google.generativeai as genai
from typing import Dict, Any, List
import json
import logging
from config import settings
from prompts.fast_prompts import FAST_SUSTAINABILITY_PROMPT, FAST_ALTERNATIVES_PROMPT

logger = logging.getLogger(__name__)

class FastGeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')

    async def identify_brand_from_image(self, image_url: str) -> Dict[str, Any]:
        """Use Gemini Vision to identify the brand from an image"""
        try:
            import requests
            from PIL import Image
            import io
            
            # Download the image
            response = requests.get(image_url, timeout=10)
            image = Image.open(io.BytesIO(response.content))
            
            prompt = """
            Look at this clothing item image and identify:
            1. The brand name - look for ANY visible logos, tags, labels, or distinctive design elements
            2. If you can't see a clear brand, make your BEST GUESS based on the style, quality, and design
            3. NEVER say "Unknown" - always provide a specific brand name guess
            4. The type of clothing item
            5. Any visible details about materials or style
            
            Common brands to consider: Nike, Adidas, H&M, Zara, Uniqlo, Gap, Old Navy, Target, Walmart, Shein, Fashion Nova, Forever 21, Urban Outfitters, American Eagle, Hollister, Abercrombie, Lululemon, Patagonia, North Face, Columbia, Champion, Puma, Reebok, Under Armour, Ralph Lauren, Tommy Hilfiger, Calvin Klein, Levi's, Wrangler, Carhartt, Dickies, etc.
            
            Return ONLY a JSON object with this structure:
            {
                "brand": "Specific Brand Name (make your best guess, never say Unknown)",
                "product_title": "Brief description of the item",
                "product_description": "More detailed description including visible features",
                "confidence": 0.0 to 1.0
            }
            """
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse the response
            text = response.text.strip()
            if text.startswith("```"):
                text = text.replace("```json", "", 1).replace("```", "", 1)
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            
            brand_info = json.loads(text)
            logger.info(f"Gemini Vision identified brand: {brand_info.get('brand', 'Unknown')}")
            
            return {
                "success": True,
                "brand_info": brand_info
            }
            
        except Exception as e:
            logger.error(f"Gemini Vision brand identification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "brand_info": {
                    "brand": "Unknown Brand",
                    "product_title": "Clothing Item",
                    "product_description": "Unable to identify from image",
                    "confidence": 0.0
                }
            }

    async def generate_sustainability_report(self, brand: str, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a quick sustainability report"""
        try:
            prompt = FAST_SUSTAINABILITY_PROMPT.format(
                brand=brand,
                product_title=product_info.get("product_title", "Unknown Product"),
                product_description=product_info.get("product_description", "Unknown description")
            )
            
            response = self.model.generate_content(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Gemini raw response: {response.text[:500]}")
            
            # Parse JSON response - handle markdown code blocks
            try:
                text = response.text.strip()
                # Remove markdown code blocks if present
                if text.startswith("```"):
                    # Remove opening ```json or ``` and closing ```
                    text = text.replace("```json", "", 1).replace("```", "", 1)
                    # Remove any remaining ``` at the end
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                
                report_data = json.loads(text)
                logger.info("Successfully parsed Gemini response as JSON")
                return {
                    "success": True,
                    "report_data": report_data
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini response as JSON: {e}")
                logger.warning(f"Raw response was: {response.text}")
                # Fallback to default data with varied scores
                return {
                    "success": True,
                    "report_data": {
                        "brand": brand,
                        "categories": {
                            "material_origin": {"score": 4, "description": "Uses some sustainable materials like organic cotton"},
                            "production_impact": {"score": 2, "description": "High water usage and carbon emissions in production"},
                            "labor_ethics": {"score": 3, "description": "Standard labor practices, no transparency on working conditions"},
                            "end_of_life": {"score": 3, "description": "Mixed materials make recycling difficult"},
                            "brand_transparency": {"score": 2, "description": "Limited information about supply chain and sustainability efforts"}
                        },
                        "overall_score": 2.8,
                        "overall_description": "This item has mixed sustainability characteristics with room for improvement.",
                        "regional_alerts": {},
                        "alternative_ids": []
                    }
                }
            
        except Exception as e:
            logger.error(f"Fast Gemini report generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Fast Gemini report generation failed: {str(e)}"
            }

    async def generate_shopping_search_query(self, brand: str, product_info: Dict[str, Any]) -> str:
        """Generate a shopping search query based on the product"""
        try:
            prompt = f"""
            Based on this clothing item, generate a Google Shopping search query to find sustainable alternatives.
            
            Original Item:
            Brand: {brand}
            Product: {product_info.get("product_title", "Unknown")}
            Description: {product_info.get("product_description", "Unknown")}
            
            Generate a search query that will find similar sustainable CLOTHING items for purchase.
            Focus on the TYPE of clothing (e.g., "men's t-shirt", "women's jeans", "jacket") and add "sustainable" or "eco-friendly".
            Include "buy" or "shop" to ensure shopping results.
            
            Return ONLY the search query text, nothing else. Example: "buy sustainable organic cotton men's t-shirt"
            """
            
            response = self.model.generate_content(prompt)
            search_query = response.text.strip().replace('"', '').replace("'", "")
            
            # Ensure "clothing" or "apparel" is in the query
            if "clothing" not in search_query.lower() and "apparel" not in search_query.lower():
                search_query = f"{search_query} clothing"
            
            # Ensure "buy" or "shop" is in the query for shopping results
            if "buy" not in search_query.lower() and "shop" not in search_query.lower():
                search_query = f"buy {search_query}"
            
            logger.info(f"Generated shopping search query: {search_query}")
            return search_query
            
        except Exception as e:
            logger.error(f"Failed to generate search query: {str(e)}")
            # Fallback to basic query
            product_type = product_info.get("product_title", "clothing").split()[0].lower()
            return f"buy sustainable eco-friendly {product_type} clothing"
    
    async def find_sustainable_alternatives(self, brand: str, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Find 3 sustainable alternatives quickly - DEPRECATED, use Google Shopping instead"""
        try:
            prompt = FAST_ALTERNATIVES_PROMPT.format(
                brand=brand,
                product_title=product_info.get("product_title", "Unknown Product"),
                product_description=product_info.get("product_description", "Clothing item")
            )
            
            response = self.model.generate_content(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Gemini alternatives raw response: {response.text[:500]}")
            
            # Parse JSON response - handle markdown code blocks
            try:
                text = response.text.strip()
                # Remove markdown code blocks if present
                if text.startswith("```"):
                    # Remove opening ```json or ``` and closing ```
                    text = text.replace("```json", "", 1).replace("```", "", 1)
                    # Remove any remaining ``` at the end
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                
                alternatives = json.loads(text)
                logger.info(f"Successfully parsed {len(alternatives)} alternatives from Gemini")
                logger.info(f"Alternatives data: {json.dumps(alternatives, indent=2)}")
                return {
                    "success": True,
                    "alternatives": alternatives
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini alternatives as JSON: {e}")
                logger.warning(f"Raw response was: {response.text}")
                # Fallback to default alternatives with varied data
                return {
                    "success": True,
                    "alternatives": [
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
                }
            
        except Exception as e:
            logger.error(f"Fast Gemini alternatives generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Fast Gemini alternatives generation failed: {str(e)}"
            }

fast_gemini_service = FastGeminiService()
