"""
Prompt templates for Gemini AI sustainability analysis
"""

SUSTAINABILITY_REPORT_PROMPT = """
You are a sustainability expert analyzing fashion items. Based on the following information, create a detailed sustainability report.

Brand: {brand}
Product: {product_title}
Description: {product_description}
{image_context}

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

ALTERNATIVES_PROMPT = """
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

# Additional prompt for image analysis
IMAGE_ANALYSIS_PROMPT = """
Analyze this fashion image and identify:
1. The type of clothing item (shirt, pants, dress, etc.)
2. The likely brand based on visual cues
3. The style and materials visible
4. Any sustainability indicators (organic labels, eco-friendly tags, etc.)

Provide a brief description that can be used for sustainability analysis.
"""
