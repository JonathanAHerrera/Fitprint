import google.generativeai as genai
from typing import Dict, Any, List
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def generate_sustainability_report(self, brand: str, product_info: Dict[str, Any], image_url: str = None) -> Dict[str, Any]:
        """Generate a sustainability report using Gemini AI"""
        try:
            prompt = self._build_sustainability_prompt(brand, product_info, image_url)
            
            response = self.model.generate_content(prompt)
            
            # Parse the response to extract structured data
            report_data = self._parse_sustainability_response(response.text)
            
            return {
                "success": True,
                "report_data": report_data
            }
            
        except Exception as e:
            logger.error(f"Gemini sustainability report generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Gemini report generation failed: {str(e)}"
            }

    async def find_sustainable_alternatives(self, brand: str, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Find 3 sustainable alternatives using Gemini AI"""
        try:
            prompt = self._build_alternatives_prompt(brand, product_info)
            
            response = self.model.generate_content(prompt)
            
            # Parse the response to extract alternatives
            alternatives = self._parse_alternatives_response(response.text)
            
            return {
                "success": True,
                "alternatives": alternatives
            }
            
        except Exception as e:
            logger.error(f"Gemini alternatives generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Gemini alternatives generation failed: {str(e)}"
            }

    def _build_sustainability_prompt(self, brand: str, product_info: Dict[str, Any], image_url: str = None) -> str:
        """Build the prompt for sustainability report generation"""
        product_title = product_info.get('product_title', 'Unknown Product')
        product_description = product_info.get('product_description', 'No description available')
        
        prompt = f"""
You are a sustainability expert analyzing fashion items. Based on the following information, create a detailed sustainability report.

Brand: {brand}
Product: {product_title}
Description: {product_description}
{f"Image URL: {image_url}" if image_url else ""}

Please analyze this item and provide a sustainability report in the following JSON format:

{{
    "brand": "{brand}",
    "categories": {{
        "material_origin": {{
            "score": <integer 1-5>,
            "description": "<detailed explanation>"
        }},
        "production_impact": {{
            "score": <integer 1-5>,
            "description": "<detailed explanation>"
        }},
        "labor_ethics": {{
            "score": <integer 1-5>,
            "description": "<detailed explanation>"
        }},
        "end_of_life": {{
            "score": <integer 1-5>,
            "description": "<detailed explanation>"
        }},
        "brand_transparency": {{
            "score": <integer 1-5>,
            "description": "<detailed explanation>"
        }}
    }},
    "overall_score": <float 1.0-5.0>,
    "overall_description": "<comprehensive sustainability assessment>",
    "regional_alerts": {{
        "EU": "<any EU-specific regulations or alerts>",
        "CA": "<any Canada-specific regulations or alerts>",
        "US": "<any US-specific regulations or alerts>",
        "UK": "<any UK-specific regulations or alerts>"
    }}
}}

Scoring Guidelines:
- 1: Very poor (major sustainability issues)
- 2: Poor (significant concerns)
- 3: Fair (some positive aspects, room for improvement)
- 4: Good (strong sustainability practices)
- 5: Excellent (outstanding sustainability leadership)

Focus on:
- Material sourcing and sustainability
- Production processes and environmental impact
- Labor practices and worker rights
- End-of-life disposal and circularity
- Brand transparency and reporting

Provide realistic, research-based assessments. If you don't have specific information about the brand, make reasonable inferences based on industry standards and brand reputation.
"""
        return prompt

    def _build_alternatives_prompt(self, brand: str, product_info: Dict[str, Any]) -> str:
        """Build the prompt for finding sustainable alternatives"""
        product_title = product_info.get('product_title', 'Unknown Product')
        
        prompt = f"""
You are a sustainability expert helping consumers find more sustainable alternatives to fashion items.

Original Item:
Brand: {brand}
Product: {product_title}

Please suggest 3 sustainable alternatives that are:
1. More environmentally friendly
2. Better labor practices
3. More transparent supply chains
4. Better end-of-life options

Provide your response in the following JSON format:

{{
    "alternatives": [
        {{
            "name": "<product name>",
            "brand": "<brand name>",
            "image_url": "<product image URL>",
            "sustainability_score": <float 1.0-5.0>,
            "link": "<purchase link>",
            "why_sustainable": "<brief explanation of why this is more sustainable>"
        }},
        {{
            "name": "<product name>",
            "brand": "<brand name>",
            "image_url": "<product image URL>",
            "sustainability_score": <float 1.0-5.0>,
            "link": "<purchase link>",
            "why_sustainable": "<brief explanation of why this is more sustainable>"
        }},
        {{
            "name": "<product name>",
            "brand": "<brand name>",
            "image_url": "<product image URL>",
            "sustainability_score": <float 1.0-5.0>,
            "link": "<purchase link>",
            "why_sustainable": "<brief explanation of why this is more sustainable>"
        }}
    ]
}}

Focus on:
- Sustainable materials (organic cotton, recycled materials, etc.)
- Ethical brands with good labor practices
- Local or regional options when possible
- Brands with strong sustainability certifications
- Second-hand or vintage options
- Brands with transparent supply chains

Provide realistic, purchasable alternatives with actual brand names and products.
"""
        return prompt

    def _parse_sustainability_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response to extract sustainability report data"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create a basic structure
                return self._create_fallback_report()
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse Gemini response as JSON, using fallback")
            return self._create_fallback_report()

    def _parse_alternatives_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Gemini response to extract alternatives data"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                return data.get('alternatives', [])
            else:
                return self._create_fallback_alternatives()
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse Gemini alternatives response as JSON, using fallback")
            return self._create_fallback_alternatives()

    def _create_fallback_report(self) -> Dict[str, Any]:
        """Create a fallback sustainability report when parsing fails"""
        return {
            "brand": "Unknown",
            "categories": {
                "material_origin": {
                    "score": 3,
                    "description": "Unable to determine material sourcing practices"
                },
                "production_impact": {
                    "score": 3,
                    "description": "Unable to assess production environmental impact"
                },
                "labor_ethics": {
                    "score": 3,
                    "description": "Unable to verify labor practices"
                },
                "end_of_life": {
                    "score": 3,
                    "description": "Unable to assess end-of-life options"
                },
                "brand_transparency": {
                    "score": 3,
                    "description": "Unable to assess brand transparency"
                }
            },
            "overall_score": 3.0,
            "overall_description": "Unable to generate detailed sustainability assessment",
            "regional_alerts": {
                "EU": None,
                "CA": None,
                "US": None,
                "UK": None
            }
        }

    def _create_fallback_alternatives(self) -> List[Dict[str, Any]]:
        """Create fallback alternatives when parsing fails"""
        return [
            {
                "name": "Sustainable Alternative 1",
                "brand": "EcoBrand",
                "image_url": "",
                "sustainability_score": 4.0,
                "link": "",
                "why_sustainable": "Made with organic materials and fair trade practices"
            },
            {
                "name": "Sustainable Alternative 2", 
                "brand": "GreenFashion",
                "image_url": "",
                "sustainability_score": 4.2,
                "link": "",
                "why_sustainable": "Recycled materials and carbon-neutral production"
            },
            {
                "name": "Sustainable Alternative 3",
                "brand": "EthicalWear",
                "image_url": "",
                "sustainability_score": 4.5,
                "link": "",
                "why_sustainable": "Local production with transparent supply chain"
            }
        ]

gemini_service = GeminiService()
