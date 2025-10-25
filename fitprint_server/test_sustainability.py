#!/usr/bin/env python3
import requests
import json

# Test data for sustainability report
test_report = {
    "clothing_id": "cl_48291",
    "brand": "Sex Pot Revenge",
    "categories": {
        "material_origin": {
            "score": 2,
            "description": "Made mostly of non-recyclable synthetics with no sustainable sourcing info."
        },
        "production_impact": {
            "score": 3,
            "description": "Average impact with some eco-efficiency efforts such as reduced water use."
        },
        "labor_ethics": {
            "score": 1,
            "description": "No transparency on labor practices; high risk of exploitation."
        },
        "end_of_life": {
            "score": 2,
            "description": "Partially recyclable materials but limited re-use potential."
        },
        "brand_transparency": {
            "score": 1,
            "description": "No publicly available supply-chain or sustainability data."
        }
    },
    "overall_score": 1.8,
    "overall_description": "This item lacks sustainable sourcing and transparency; high environmental impact.",
    "regional_alerts": {
        "EU": "Digital Product Passport 2027",
        "CA": "EPR textile recycling bill pending"
    },
    "alternative_ids": [
        "alt_302",
        "alt_401", 
        "alt_578"
    ]
}

def test_sustainability_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Sustainability API...")
    
    try:
        # Test creating a sustainability report
        print("\n📊 Creating sustainability report...")
        response = requests.post(
            f"{base_url}/sustainability/reports",
            json=test_report,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully created sustainability report!")
            print(f"📋 Report ID: {result.get('report_id')}")
            print(f"📝 Message: {result.get('message')}")
            
            # Test getting the report
            report_id = result.get('report_id')
            if report_id:
                print(f"\n🔍 Retrieving report {report_id}...")
                get_response = requests.get(f"{base_url}/sustainability/reports/{report_id}")
                
                if get_response.status_code == 200:
                    report_data = get_response.json()
                    print("✅ Successfully retrieved report!")
                    print(f"🏷️  Brand: {report_data.get('brand')}")
                    print(f"📊 Overall Score: {report_data.get('overall_score')}")
                    print(f"📝 Description: {report_data.get('overall_description')}")
                else:
                    print(f"❌ Failed to retrieve report: {get_response.status_code}")
                    print(get_response.text)
            
            # Test getting reports by clothing ID
            print(f"\n🔍 Getting reports for clothing ID: {test_report['clothing_id']}...")
            clothing_response = requests.get(f"{base_url}/sustainability/reports/clothing/{test_report['clothing_id']}")
            
            if clothing_response.status_code == 200:
                clothing_data = clothing_response.json()
                print("✅ Successfully retrieved reports by clothing ID!")
                print(f"📊 Found {clothing_data.get('count')} reports")
            else:
                print(f"❌ Failed to get reports by clothing ID: {clothing_response.status_code}")
                print(clothing_response.text)
            
            # Test sustainability summary
            print(f"\n📈 Getting sustainability summary...")
            summary_response = requests.get(f"{base_url}/sustainability/scores/summary")
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                print("✅ Successfully retrieved sustainability summary!")
                print(f"📊 Total Reports: {summary_data.get('total_reports')}")
                print(f"📈 Average Score: {summary_data.get('average_score')}")
                print(f"📊 Score Distribution: {summary_data.get('score_distribution')}")
            else:
                print(f"❌ Failed to get summary: {summary_response.status_code}")
                print(summary_response.text)
                
        else:
            print(f"❌ Failed to create report: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sustainability_api()
