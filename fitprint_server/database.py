import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional
from config import settings
import json
from decimal import Decimal

class DynamoDBService:
    def __init__(self):
        # Initialize DynamoDB client
        dynamodb_kwargs = {
            'region_name': settings.AWS_REGION
        }
        
        # Add credentials if provided
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            dynamodb_kwargs.update({
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
            })
        
        # Add endpoint URL for local development
        if settings.DYNAMODB_ENDPOINT_URL:
            dynamodb_kwargs['endpoint_url'] = settings.DYNAMODB_ENDPOINT_URL
            
        self.dynamodb = boto3.resource('dynamodb', **dynamodb_kwargs)
        self.clothing_table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
        self.sustainability_table = self.dynamodb.Table('sustainability-reports')
        self.alternatives_table = self.dynamodb.Table('alternatives')
    
    def _convert_floats_to_decimal(self, obj):
        """Convert float values to Decimal for DynamoDB compatibility"""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        else:
            return obj
    
    async def create_item(self, item: Dict[str, Any], table_name: str = "clothing") -> Dict[str, Any]:
        """Create a new item in DynamoDB"""
        try:
            if table_name == "clothing":
                table = self.clothing_table
            elif table_name == "sustainability":
                table = self.sustainability_table
            elif table_name == "alternatives":
                table = self.alternatives_table
            else:
                return {"success": False, "error": f"Unknown table: {table_name}"}
            
            # Convert floats to Decimal for DynamoDB compatibility
            converted_item = self._convert_floats_to_decimal(item)
            response = table.put_item(Item=converted_item)
            return {"success": True, "item": item, "response": response}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def get_item(self, key: Dict[str, Any], table_name: str = "clothing") -> Dict[str, Any]:
        """Get an item by its key"""
        try:
            if table_name == "clothing":
                table = self.clothing_table
            elif table_name == "sustainability":
                table = self.sustainability_table
            elif table_name == "alternatives":
                table = self.alternatives_table
            else:
                return {"success": False, "error": f"Unknown table: {table_name}"}
            
            response = table.get_item(Key=key)
            if 'Item' in response:
                return {"success": True, "item": response['Item']}
            else:
                return {"success": False, "error": "Item not found"}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def update_item(self, key: Dict[str, Any], update_expression: str, 
                         expression_attribute_values: Dict[str, Any], table_name: str = "clothing") -> Dict[str, Any]:
        """Update an item in DynamoDB"""
        try:
            if table_name == "clothing":
                table = self.clothing_table
            elif table_name == "sustainability":
                table = self.sustainability_table
            elif table_name == "alternatives":
                table = self.alternatives_table
            else:
                return {"success": False, "error": f"Unknown table: {table_name}"}
            
            response = table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"
            )
            return {"success": True, "response": response}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def delete_item(self, key: Dict[str, Any], table_name: str = "clothing") -> Dict[str, Any]:
        """Delete an item from DynamoDB"""
        try:
            if table_name == "clothing":
                table = self.clothing_table
            elif table_name == "sustainability":
                table = self.sustainability_table
            elif table_name == "alternatives":
                table = self.alternatives_table
            else:
                return {"success": False, "error": f"Unknown table: {table_name}"}
            
            response = table.delete_item(Key=key)
            return {"success": True, "response": response}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def scan_table(self, limit: int = 100, table_name: str = "clothing") -> Dict[str, Any]:
        """Scan all items in the table"""
        try:
            if table_name == "clothing":
                table = self.clothing_table
            elif table_name == "sustainability":
                table = self.sustainability_table
            elif table_name == "alternatives":
                table = self.alternatives_table
            else:
                return {"success": False, "error": f"Unknown table: {table_name}"}
            
            response = table.scan(Limit=limit)
            return {"success": True, "items": response.get('Items', [])}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def query_items(self, key_condition_expression: str, 
                         expression_attribute_values: Dict[str, Any], table_name: str = "clothing") -> Dict[str, Any]:
        """Query items with a key condition"""
        try:
            if table_name == "clothing":
                table = self.clothing_table
            elif table_name == "sustainability":
                table = self.sustainability_table
            elif table_name == "alternatives":
                table = self.alternatives_table
            else:
                return {"success": False, "error": f"Unknown table: {table_name}"}
            
            response = table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return {"success": True, "items": response.get('Items', [])}
        except ClientError as e:
            return {"success": False, "error": str(e)}

# Create a global instance
dynamodb_service = DynamoDBService()
