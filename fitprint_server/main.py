"""Fitprint API entrypoint with clothing management and Google sign-in."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel

from api.models import ItemCreate, ItemUpdate
from api.routes.clothing_routes import router as clothing_router
from config import settings
from database import dynamodb_service


load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
USERS_TABLE_NAME = os.getenv("USERS_TABLE_NAME")

if not GOOGLE_CLIENT_ID:
    raise RuntimeError("Missing GOOGLE_CLIENT_ID environment variable for Google sign-in.")
if not USERS_TABLE_NAME:
    raise RuntimeError("Missing USERS_TABLE_NAME environment variable for DynamoDB storage.")


app = FastAPI(title="Fitprint API", description="API for Fitprint fitness tracking app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to known origins before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routers
app.include_router(clothing_router)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello World", "api": "Fitprint API"}


# Generic DynamoDB CRUD endpoints leveraging the shared service -----------------

@app.post("/items")
async def create_item(item: ItemCreate) -> Dict[str, Any]:
    """Create a new item in DynamoDB."""

    result = await dynamodb_service.create_item(item.data)
    if result["success"]:
        return result
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])


@app.get("/items/{clothing_id}")
async def get_item(clothing_id: str, brand: str | None = None) -> Dict[str, Any]:
    """Retrieve an item by primary key."""

    key: Dict[str, Any] = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.get_item(key)
    if result["success"]:
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])


@app.put("/items/{clothing_id}")
async def update_item(clothing_id: str, update_data: ItemUpdate, brand: str | None = None) -> Dict[str, Any]:
    """Update an item in DynamoDB."""

    key: Dict[str, Any] = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.update_item(
        key,
        update_data.update_expression,
        update_data.expression_attribute_values,
    )
    if result["success"]:
        return result
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])


@app.delete("/items/{clothing_id}")
async def delete_item(clothing_id: str, brand: str | None = None) -> Dict[str, str]:
    """Delete an item from DynamoDB."""

    key: Dict[str, Any] = {"clothing_id": clothing_id}
    if brand:
        key["brand"] = brand
    result = await dynamodb_service.delete_item(key)
    if result["success"]:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])


@app.get("/items")
async def list_items(limit: int = 100) -> Dict[str, Any]:
    """List items in the table."""

    result = await dynamodb_service.scan_table(limit)
    if result["success"]:
        return result
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"])


# Google sign-in support -------------------------------------------------------

dynamodb_kwargs: Dict[str, Any] = {"region_name": settings.AWS_REGION}
if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
    dynamodb_kwargs.update(
        {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        }
    )
if settings.DYNAMODB_ENDPOINT_URL:
    dynamodb_kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL

dynamodb_resource = boto3.resource("dynamodb", **dynamodb_kwargs)
users_table = dynamodb_resource.Table(USERS_TABLE_NAME)
google_request = google_requests.Request()


class GoogleLoginRequest(BaseModel):
    """Payload expected from the mobile app after Google OAuth completes."""

    id_token: str


class AuthenticatedUser(BaseModel):
    """Response payload returned to the mobile client."""

    user_id: str
    email: str | None = None
    full_name: str | None = None
    picture: str | None = None
    last_login: datetime


def verify_google_id_token(token: str) -> Dict[str, Any]:
    """Validate the Google ID token and return its claims."""

    try:
        return id_token.verify_oauth2_token(token, google_request, GOOGLE_CLIENT_ID)
    except ValueError as exc:  # token invalid/expired/mismatched audience
        logger.warning("Invalid Google ID token: %s", exc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token")


def upsert_user(claims: Dict[str, Any]) -> Dict[str, Any]:
    """Persist the Google user in DynamoDB and return the stored item."""

    now = datetime.now(timezone.utc).isoformat()
    item_key = {"user_id": claims["sub"]}
    update_expression = (
        "SET email = :email, full_name = :full_name, picture = :picture, "
        "provider = :provider, last_login = :last_login, "
        "created_at = if_not_exists(created_at, :created_at)"
    )
    expression_values = {
        ":email": claims.get("email"),
        ":full_name": claims.get("name"),
        ":picture": claims.get("picture"),
        ":provider": "google",
        ":last_login": now,
        ":created_at": now,
        ":inc": 1,
    }

    try:
        response = users_table.update_item(
            Key=item_key,
            UpdateExpression=update_expression + " ADD login_count :inc",
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW",
        )
    except ClientError as exc:  # DynamoDB unavailable/misconfigured
        logger.exception("Failed to upsert user in DynamoDB")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to store user profile") from exc

    attributes = response.get("Attributes") or {}
    logger.info("Upserted user %s", attributes.get("user_id"))
    return attributes


def fetch_user(user_id: str) -> Dict[str, Any] | None:
    """Retrieve a previously stored user record."""

    try:
        response = users_table.get_item(Key={"user_id": user_id})
    except ClientError as exc:
        logger.exception("Failed to fetch user from DynamoDB")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to load user profile") from exc

    return response.get("Item")


def get_bearer_token(authorization: str = Header(default="")) -> str:
    """Extract the bearer token from the Authorization header."""

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1]


@app.on_event("startup")
def validate_startup() -> None:
    """Ensure DynamoDB access is healthy before serving traffic."""

    try:
        users_table.table_status  # lazy call that raises if table is missing
    except ClientError as exc:
        logger.exception("DynamoDB users table misconfigured")
        raise RuntimeError("Unable to access USERS_TABLE_NAME in DynamoDB. Double-check the table name and AWS IAM permissions.") from exc


@app.get("/health", tags=["system"])
async def healthcheck() -> Dict[str, str]:
    """Basic liveness probe for monitoring."""

    return {"status": "ok"}


@app.post("/auth/google", response_model=AuthenticatedUser, tags=["auth"], summary="Sign in with Google")
async def authenticate_with_google(payload: GoogleLoginRequest) -> AuthenticatedUser:
    """Validate the Google ID token and persist the user profile."""

    claims = verify_google_id_token(payload.id_token)
    stored_user = upsert_user(claims)

    return AuthenticatedUser(
        user_id=stored_user["user_id"],
        email=stored_user.get("email"),
        full_name=stored_user.get("full_name"),
        picture=stored_user.get("picture"),
        last_login=datetime.fromisoformat(stored_user["last_login"]),
    )


@app.get("/auth/me", response_model=AuthenticatedUser, tags=["auth"], summary="Return the current user")
async def get_authenticated_user(token: str = Depends(get_bearer_token)) -> AuthenticatedUser:
    """Return the current user based on an existing Google ID token."""

    claims = verify_google_id_token(token)
    stored_user = fetch_user(claims["sub"]) or upsert_user(claims)

    return AuthenticatedUser(
        user_id=stored_user["user_id"],
        email=stored_user.get("email"),
        full_name=stored_user.get("full_name"),
        picture=stored_user.get("picture"),
        last_login=datetime.fromisoformat(stored_user["last_login"]),
    )
