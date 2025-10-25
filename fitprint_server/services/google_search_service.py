from googleapiclient.discovery import build
from typing import Dict, Any, List, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class GoogleSearchService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.service = build("customsearch", "v1", developerKey=self.api_key)

    async def reverse_image_search(self, image_url: str) -> Dict[str, Any]:
        """Perform reverse image search using Google Custom Search API"""
        try:
            # Use the image URL for reverse search
            search_params = {
                'q': image_url,
                'cx': self.search_engine_id,
                'searchType': 'image',
                'num': 10,  # Get top 10 results
                'imgType': 'photo',
                'imgSize': 'medium'
            }
            
            # Perform the search
            result = self.service.cse().list(**search_params).execute()
            
            # Parse results to extract brand and product information
            search_results = result.get('items', [])
            brand_info = self._extract_brand_info(search_results)
            
            return {
                "success": True,
                "brand_info": brand_info,
                "search_results": search_results,
                "total_results": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return {
                "success": False,
                "error": f"Google search failed: {str(e)}"
            }

    def _extract_brand_info(self, search_results: List[Dict]) -> Dict[str, Any]:
        """Extract brand and product information from search results"""
        brands = {}
        products = []
        
        for item in search_results:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            
            # Extract brand names (common fashion brands)
            brand_keywords = [
                'nike', 'adidas', 'puma', 'under armour', 'lululemon', 'patagonia',
                'north face', 'columbia', 'gap', 'h&m', 'zara', 'uniqlo', 'target',
                'walmart', 'amazon', 'shein', 'fashion nova', 'urban outfitters',
                'forever 21', 'hollister', 'abercrombie', 'calvin klein', 'tommy hilfiger',
                'ralph lauren', 'levi\'s', 'wrangler', 'dickies', 'carhartt'
            ]
            
            # Check for brand mentions
            text_to_search = f"{title} {snippet}".lower()
            for brand in brand_keywords:
                if brand in text_to_search:
                    brands[brand] = brands.get(brand, 0) + 1
            
            # Extract product information
            product_info = {
                'title': title,
                'snippet': snippet,
                'link': link,
                'image_url': item.get('image', {}).get('src', '')
            }
            products.append(product_info)
        
        # Find most likely brand
        most_likely_brand = max(brands.items(), key=lambda x: x[1])[0] if brands else None
        
        # Extract product details from the most relevant result
        best_match = products[0] if products else {}
        
        return {
            'brand': most_likely_brand,
            'confidence': max(brands.values()) / len(search_results) if brands else 0,
            'product_title': best_match.get('title', ''),
            'product_description': best_match.get('snippet', ''),
            'product_link': best_match.get('link', ''),
            'product_image': best_match.get('image_url', ''),
            'all_brands_found': list(brands.keys()),
            'total_matches': len(products)
        }

    async def search_by_text(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search for products by text query"""
        try:
            search_params = {
                'q': query,
                'cx': self.search_engine_id,
                'num': num_results,
                'searchType': 'image'
            }
            
            result = self.service.cse().list(**search_params).execute()
            search_results = result.get('items', [])
            
            return {
                "success": True,
                "results": search_results,
                "total_results": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Text search failed: {str(e)}")
            return {
                "success": False,
                "error": f"Text search failed: {str(e)}"
            }

google_search_service = GoogleSearchService()
