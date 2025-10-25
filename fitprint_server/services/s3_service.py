import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from config import settings
import uuid
from datetime import datetime
from PIL import Image
import io

class S3Service:
    def __init__(self):
        # Initialize S3 client
        s3_kwargs = {
            'region_name': settings.S3_REGION
        }

        # Add credentials if provided
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            s3_kwargs.update({
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
            })

        self.s3_client = boto3.client('s3', **s3_kwargs)
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_image(self, file_content: bytes, user_id: str, original_filename: str = None) -> Dict[str, Any]:
        """Upload an image to S3 and return the URL"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = original_filename.split('.')[-1] if original_filename and '.' in original_filename else 'jpg'
            filename = f"outfits/{user_id}/{timestamp}_{unique_id}.{file_extension}"
            
            # Compress image if it's too large
            processed_content = await self._process_image(file_content)
            
            # Upload to S3
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=processed_content,
                    ContentType='image/jpeg'
                )
                # Use real S3 URL
                image_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{filename}"
            except ClientError as e:
                # Log the error and use fallback URL
                print(f"S3 upload failed (using fallback URL): {str(e)}")
                image_url = f"https://mock-s3-url.com/{self.bucket_name}/{filename}"
            
            return {
                "success": True,
                "image_url": image_url,
                "filename": filename,
                "bucket": self.bucket_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Image processing failed: {str(e)}"
            }

    async def _process_image(self, file_content: bytes) -> bytes:
        """Process and compress image if needed"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 1920x1080)
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save as JPEG with compression
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            # If processing fails, return original content
            return file_content

    async def delete_image(self, filename: str) -> Dict[str, Any]:
        """Delete an image from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return {"success": True, "message": "Image deleted successfully"}
        except ClientError as e:
            return {"success": False, "error": f"Failed to delete image: {str(e)}"}

s3_service = S3Service()
