import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional
from config import settings
import json

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
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
    
    async def create_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in DynamoDB"""
        try:
            response = self.table.put_item(Item=item)
            return {"success": True, "item": item, "response": response}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def get_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        """Get an item by its key"""
        try:
            response = self.table.get_item(Key=key)
            if 'Item' in response:
                return {"success": True, "item": response['Item']}
            else:
                return {"success": False, "error": "Item not found"}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def update_item(self, key: Dict[str, Any], update_expression: str, 
                         expression_attribute_values: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item in DynamoDB"""
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"
            )
            return {"success": True, "response": response}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def delete_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an item from DynamoDB"""
        try:
            response = self.table.delete_item(Key=key)
            return {"success": True, "response": response}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def scan_table(self, limit: int = 100) -> Dict[str, Any]:
        """Scan all items in the table"""
        try:
            response = self.table.scan(Limit=limit)
            return {"success": True, "items": response.get('Items', [])}
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def query_items(self, key_condition_expression: str, 
                         expression_attribute_values: Dict[str, Any]) -> Dict[str, Any]:
        """Query items with a key condition"""
        try:
            response = self.table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return {"success": True, "items": response.get('Items', [])}
        except ClientError as e:
            return {"success": False, "error": str(e)}

# Create a global instance
dynamodb_service = DynamoDBService()
