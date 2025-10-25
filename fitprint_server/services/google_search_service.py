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
                'imgType': 'photo'
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
    
    async def search_shopping_results(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """Search for shopping results with images and links"""
        try:
            logger.info(f"Searching for shopping results: {query}")
            
            # Search for more results than needed so we can filter
            search_params = {
                'q': query,
                'cx': self.search_engine_id,
                'num': 10,  # Get more results to filter
            }
            
            result = self.service.cse().list(**search_params).execute()
            search_results = result.get('items', [])
            
            # Parse results into a clean format
            alternatives = []
            for item in search_results:
                title = item.get('title', 'Product')
                link = item.get('link', '')
                snippet = item.get('snippet', '')
                
                # Filter out non-shopping sites
                if not self._is_valid_clothing_store(link, title):
                    logger.info(f"Filtered out non-store result: {link}")
                    continue
                
                # Try to get image from pagemap
                image_url = ""
                pagemap = item.get('pagemap', {})
                if 'cse_image' in pagemap and len(pagemap['cse_image']) > 0:
                    image_url = pagemap['cse_image'][0].get('src', '')
                elif 'cse_thumbnail' in pagemap and len(pagemap['cse_thumbnail']) > 0:
                    image_url = pagemap['cse_thumbnail'][0].get('src', '')
                
                # Extract brand from title or link
                brand = self._extract_brand_from_text(title + " " + link)
                
                alternative = {
                    "name": title[:100],  # Limit title length
                    "brand": brand,
                    "image_url": image_url,
                    "sustainability_score": 4.0,  # Default score for sustainable search results
                    "link": link,
                    "why_sustainable": snippet[:200] if snippet else "Sustainable alternative found through eco-friendly search"
                }
                alternatives.append(alternative)
                
                # Stop once we have enough valid results
                if len(alternatives) >= num_results:
                    break
            
            logger.info(f"Found {len(alternatives)} valid shopping alternatives after filtering")
            return {
                "success": True,
                "alternatives": alternatives
            }
            
        except Exception as e:
            logger.error(f"Shopping search failed: {str(e)}")
            return {
                "success": False,
                "error": f"Shopping search failed: {str(e)}",
                "alternatives": []
            }
    
    def _is_valid_clothing_store(self, url: str, title: str) -> bool:
        """Check if the URL is from a valid clothing store"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Blacklist - sites to exclude
        blacklist = [
            'reddit.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'pinterest.com', 'youtube.com', 'tiktok.com',
            'wikipedia.org', 'wiki', 'blog', 'forum',
            'news', 'article', 'review-site', 'comparison'
        ]
        
        for blocked in blacklist:
            if blocked in url_lower:
                return False
        
        # Whitelist - known clothing/fashion stores
        clothing_stores = [
            'patagonia.com', 'tentree.com', 'everlane.com', 'reformation.com',
            'outerknown.com', 'allbirds.com', 'girlfriend.com', 'wearpact.com',
            'kotn.com', 'thought', 'peopletree.co', 'organicbasics.com',
            'armedangels.com', 'nudiejeans.com', 'veja-store.com',
            'etsy.com', 'fairindigo.com', 'alternativeapparel.com',
            'shop', 'store', 'buy', 'clothing', 'apparel', 'fashion',
            'wear', 'garment', 'outfit', 'dress', 'shirt', 'pants',
            'product', 'item', 'collection'
        ]
        
        # Check if URL or title contains clothing-related keywords
        for store_keyword in clothing_stores:
            if store_keyword in url_lower or store_keyword in title_lower:
                return True
        
        # Additional check: if title mentions clothing items
        clothing_items = [
            'shirt', 't-shirt', 'tee', 'top', 'blouse', 'sweater', 'hoodie',
            'jacket', 'coat', 'pants', 'jeans', 'shorts', 'skirt', 'dress',
            'shoes', 'sneakers', 'boots', 'socks', 'underwear', 'bra',
            'hat', 'cap', 'scarf', 'gloves', 'belt', 'bag'
        ]
        
        for item in clothing_items:
            if item in title_lower:
                return True
        
        return False
    
    def _extract_brand_from_text(self, text: str) -> str:
        """Extract brand name from text"""
        text_lower = text.lower()
        
        # List of sustainable brands to look for
        sustainable_brands = [
            'patagonia', 'tentree', 'everlane', 'reformation', 'outerknown',
            'allbirds', 'girlfriend collective', 'pact', 'kotn', 'thought',
            'people tree', 'organic basics', 'armedangels', 'nudie jeans',
            'veja', 'etsy', 'fair indigo', 'alternative apparel'
        ]
        
        for brand in sustainable_brands:
            if brand in text_lower:
                return brand.title()
        
        # If no sustainable brand found, try to extract from domain
        if 'http' in text_lower:
            try:
                domain = text_lower.split('//')[1].split('/')[0]
                domain = domain.replace('www.', '').replace('.com', '').replace('.org', '')
                return domain.title()
            except:
                pass
        
        return "Sustainable Brand"

google_search_service = GoogleSearchService()
