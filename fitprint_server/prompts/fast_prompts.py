"""
Fast, simplified prompts for quick testing
"""

FAST_SUSTAINABILITY_PROMPT = """
Analyze this clothing item for sustainability. Return ONLY valid JSON:

Brand: {brand}
Product: {product_title}

Return this JSON structure with varied scores and descriptions based on the brand and image you receive. Make sure the scores are between 1 and 5 and the descriptions/scores are realistic and different from this example:
{{
    "brand": "{brand}",
    "categories": {{
        "material_origin": {{"score": number, "description": "Uses some sustainable materials like organic cotton"}},
        "production_impact": {{"score": number, "description": "High water usage and carbon emissions in production"}},
        "labor_ethics": {{"score": number, "description": "Standard labor practices, no transparency on working conditions"}},
        "end_of_life": {{"score": number, "description": "Mixed materials make recycling difficult"}},
        "brand_transparency": {{"score": number, "description": "Limited information about supply chain and sustainability efforts"}}
    }},
    "overall_score": 2.8,
    "overall_description": "This item has mixed sustainability characteristics with room for improvement.",
    "regional_alerts": {{}},
    "alternative_ids": []
}}
"""

FAST_ALTERNATIVES_PROMPT = """
Based on this clothing item, suggest 3 REAL sustainable alternatives that match the style and type.

Original Item:
Brand: {brand}
Product: {product_title}
Description: {product_description}

Suggest REAL products from sustainable brands with:
1. Specific product names that match the style/type of the original
2. Direct product page links (format: https://brandwebsite.com/products/product-name)
3. Product image URLs if available
4. Realistic sustainability scores (4.0-5.0) based on actual brand practices
5. Specific sustainability features

Top Sustainable Brands:
- Patagonia (outdoor/casual) - https://www.patagonia.com
- Pact (organic basics) - https://wearpact.com
- Tentree (eco-friendly) - https://www.tentree.com
- Everlane (transparent) - https://www.everlane.com
- Reformation (trendy) - https://www.thereformation.com
- Outerknown (sustainable) - https://www.outerknown.com
- Allbirds (comfort) - https://www.allbirds.com
- Girlfriend Collective (recycled) - https://girlfriend.com
- Kotn (organic cotton) - https://kotn.com

Return ONLY this JSON array format:
[
    {{
        "name": "Specific Product Name matching the style",
        "brand": "Brand Name",
        "image_url": "https://cdn.example.com/product.jpg or empty string",
        "sustainability_score": 4.0-5.0,
        "link": "https://brandwebsite.com/products/specific-product-name",
        "why_sustainable": "Detailed explanation: materials, certifications, practices"
    }},
    {{
        "name": "Different Product Name",
        "brand": "Different Brand",
        "image_url": "",
        "sustainability_score": 4.0-5.0,
        "link": "https://brandwebsite.com/products/product",
        "why_sustainable": "Specific sustainability details"
    }},
    {{
        "name": "Third Product Name",
        "brand": "Third Brand",
        "image_url": "",
        "sustainability_score": 4.0-5.0,
        "link": "https://brandwebsite.com/products/item",
        "why_sustainable": "Why this is more sustainable"
    }}
]
"""
