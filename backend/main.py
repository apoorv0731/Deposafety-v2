"""
Main FastAPI application for DepoSafety V2.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Depends, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from config import get_settings
from models import (
    # User models
    UserCreate, UserUpdate, UserResponse, UserLogin, Token,
    # Property models
    PropertyCreate, PropertyUpdate, PropertyResponse,
    # Scan models
    ScanCreate, ScanUpdate, ScanResponse, ScanDetailResponse, ScanListResponse,
    ScanStatus, InspectionType,
    # Video models
    VideoUploadRequest, VideoUploadResponse, VideoUploadComplete,
    # Webhook models
    ProcessingWebhookPayload, ProcessingWebhookResponse,
    # Blockchain models
    BlockchainAnchorRequest, BlockchainAnchorResponse, BlockchainVerificationResponse,
    # Email models
    EmailRequest, EmailResponse,
    # Health
    HealthResponse, ErrorResponse
)
from database import db
from storage import storage
from blockchain import blockchain
from email_service import email_service
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user_id, get_current_user
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting DepoSafety V2 API...")
    yield
    logger.info("Shutting down DepoSafety V2 API...")


# Create FastAPI app
app = FastAPI(
    title="DepoSafety V2 API",
    description="Production-ready API for property inspection and 3D scanning",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Exception Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== Health Check ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.utcnow(),
        services={
            "database": "connected" if db.client else "disconnected",
            "storage": "connected" if storage.client else "disconnected",
            "blockchain": "connected" if blockchain.is_connected else "disconnected",
            "email": "connected" if email_service.is_configured else "disconnected"
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return await root()


# ==================== Authentication Endpoints ====================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user."""
    # Check if user exists
    existing = await db.get_user_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_data = {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "phone": user.phone,
        "is_active": user.is_active,
        "password_hash": get_password_hash(user.password),
        "created_at": datetime.utcnow().isoformat()
    }
    
    created = await db.create_user(user_data)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Send welcome email
    await email_service.send_welcome(
        to_email=user.email,
        full_name=user.full_name
    )
    
    return UserResponse(**created)


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token."""
    user = await db.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        },
        expires_delta=timedelta(hours=24)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user_id)):
    """Get current user profile."""
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user)


# ==================== User Endpoints ====================

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List all users (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = await db.list_users(limit=limit, offset=offset)
    return [UserResponse(**u) for u in users]


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get user by ID."""
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user)


@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user profile."""
    # Only allow users to update their own profile (or admin)
    if user_id != current_user_id:
        current_user = await db.get_user_by_id(current_user_id)
        if not current_user or current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own profile"
            )
    
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated = await db.update_user(user_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**updated)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user (admin only or self)."""
    if user_id != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own account"
        )
    
    success = await db.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None


# ==================== Property Endpoints ====================

@app.post("/properties", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new property."""
    property_dict = property_data.dict()
    property_dict["owner_id"] = property_data.owner_id or current_user_id
    property_dict["created_at"] = datetime.utcnow().isoformat()
    
    created = await db.create_property(property_dict)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create property"
        )
    
    return PropertyResponse(**created)


@app.get("/properties", response_model=List[PropertyResponse])
async def list_properties(
    owner_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id)
):
    """List properties with optional owner filter."""
    properties = await db.list_properties(
        owner_id=owner_id,
        limit=limit,
        offset=offset
    )
    return [PropertyResponse(**p) for p in properties]


@app.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get property by ID."""
    property_data = await db.get_property_by_id(property_id)
    if not property_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    return PropertyResponse(**property_data)


@app.patch("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    property_update: PropertyUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update property."""
    # Check ownership
    existing = await db.get_property_by_id(property_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if str(existing.get("owner_id")) != current_user_id:
        current_user = await db.get_user_by_id(current_user_id)
        if not current_user or current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own properties"
            )
    
    update_data = {k: v for k, v in property_update.dict(exclude_unset=True).items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated = await db.update_property(property_id, update_data)
    return PropertyResponse(**updated)


@app.delete("/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete property."""
    existing = await db.get_property_by_id(property_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if str(existing.get("owner_id")) != current_user_id:
        current_user = await db.get_user_by_id(current_user_id)
        if not current_user or current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete your own properties"
            )
    
    success = await db.delete_property(property_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete property"
        )
    return None


# ==================== Scan Endpoints ====================

@app.post("/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new scan/inspection."""
    # Verify property exists
    property_data = await db.get_property_by_id(str(scan_data.property_id))
    if not property_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    scan_dict = scan_data.dict()
    scan_dict["inspector_id"] = current_user_id
    scan_dict["status"] = ScanStatus.PENDING.value
    scan_dict["created_at"] = datetime.utcnow().isoformat()
    
    created = await db.create_scan(scan_dict)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan"
        )
    
    return ScanResponse(**created)


@app.get("/scans", response_model=ScanListResponse)
async def list_scans(
    property_id: Optional[str] = None,
    status: Optional[ScanStatus] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id)
):
    """List scans with optional filters."""
    scans = await db.list_scans(
        property_id=property_id,
        inspector_id=current_user_id,
        status=status.value if status else None,
        limit=limit,
        offset=offset
    )
    
    total = await db.count_scans({"inspector_id": current_user_id})
    
    return ScanListResponse(
        total=total,
        scans=[ScanResponse(**s) for s in scans]
    )


@app.get("/scans/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get scan by ID with details."""
    scan = await db.get_scan_with_details(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Parse the response with joined data
    scan_response = {
        **scan,
        "property": scan.get("properties") if scan.get("properties") else None,
        "inspector": scan.get("users") if scan.get("users") else None
    }
    
    return ScanDetailResponse(**scan_response)


@app.patch("/scans/{scan_id}", response_model=ScanResponse)
async def update_scan(
    scan_id: str,
    scan_update: ScanUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update scan."""
    existing = await db.get_scan_by_id(scan_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    update_data = {k: v for k, v in scan_update.dict(exclude_unset=True).items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated = await db.update_scan(scan_id, update_data)
    return ScanResponse(**updated)


@app.delete("/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete scan."""
    existing = await db.get_scan_by_id(scan_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    success = await db.delete_scan(scan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scan"
        )
    return None


# ==================== Video Upload Endpoints ====================

@app.post("/scans/{scan_id}/upload-url", response_model=VideoUploadResponse)
async def get_upload_url(
    scan_id: str,
    filename: str = Query(..., description="Original filename"),
    content_type: str = Query("video/mp4", description="Video MIME type"),
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate a presigned URL for video upload."""
    # Verify scan exists
    scan = await db.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Generate storage key
    key = storage.generate_video_key(scan_id, filename)
    
    # Generate presigned URL
    upload_url = await storage.generate_upload_url(key, content_type)
    if not upload_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )
    
    # Update scan with video key
    await db.update_scan(scan_id, {
        "video_key": key,
        "status": ScanStatus.PROCESSING.value,
        "updated_at": datetime.utcnow().isoformat()
    })
    
    return VideoUploadResponse(
        upload_url=upload_url,
        scan_id=scan_id,
        expires_in=3600
    )


@app.post("/scans/{scan_id}/upload-complete", response_model=ScanResponse)
async def upload_complete(
    scan_id: str,
    completion: VideoUploadComplete,
    current_user_id: str = Depends(get_current_user_id)
):
    """Mark video upload as complete."""
    scan = await db.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    updated = await db.update_scan(scan_id, {
        "video_url": completion.video_url,
        "status": ScanStatus.PROCESSING.value,
        "updated_at": datetime.utcnow().isoformat()
    })
    
    return ScanResponse(**updated)


# ==================== Webhook Endpoints ====================

@app.post("/webhooks/processing-complete", response_model=ProcessingWebhookResponse)
async def processing_webhook(payload: ProcessingWebhookPayload):
    """
    Webhook endpoint for 3D processing completion.
    Called by the video processing service when 3D model generation is complete.
    """
    scan_id = payload.scan_id
    
    # Get scan
    scan = await db.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Update scan status
    update_data = {
        "status": payload.status.value,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if payload.model_3d_url:
        update_data["model_3d_url"] = payload.model_3d_url
    
    if payload.status == ScanStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow().isoformat()
    
    await db.update_scan(scan_id, update_data)
    
    # If completed successfully, trigger blockchain anchoring
    if payload.status == ScanStatus.COMPLETED:
        # Generate metadata hash
        metadata = {
            "scan_id": scan_id,
            "property_id": scan.get("property_id"),
            "inspector_id": scan.get("inspector_id"),
            "video_url": scan.get("video_url"),
            "model_3d_url": payload.model_3d_url,
            "completed_at": datetime.utcnow().isoformat()
        }
        metadata_hash = blockchain.generate_metadata_hash(metadata)
        
        # Anchor to blockchain
        anchor_result = await blockchain.anchor_inspection(scan_id, metadata_hash)
        
        if anchor_result:
            await db.update_scan(scan_id, {
                "blockchain_tx_hash": anchor_result["transaction_hash"],
                "metadata_hash": metadata_hash
            })
            
            # Send completion email
            inspector = await db.get_user_by_id(scan.get("inspector_id"))
            property_data = await db.get_property_by_id(scan.get("property_id"))
            
            if inspector and property_data:
                await email_service.send_scan_completed(
                    to_email=inspector["email"],
                    full_name=inspector["full_name"],
                    property_name=property_data["name"],
                    property_address=property_data["address"],
                    inspection_type=scan.get("inspection_type", "routine"),
                    completed_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                    blockchain_tx=anchor_result["transaction_hash"],
                    scan_url=f"https://app.deposafety.com/scans/{scan_id}"
                )
    
    return ProcessingWebhookResponse(
        success=True,
        message=f"Scan {scan_id} updated to {payload.status.value}",
        scan_id=scan_id
    )


# ==================== Blockchain Endpoints ====================

@app.post("/scans/{scan_id}/anchor", response_model=BlockchainAnchorResponse)
async def anchor_scan(
    scan_id: str,
    request: BlockchainAnchorRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Manually anchor a scan to the blockchain."""
    scan = await db.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Anchor to blockchain
    result = await blockchain.anchor_inspection(scan_id, request.metadata_hash)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to anchor to blockchain"
        )
    
    # Update scan with transaction hash
    await db.update_scan(scan_id, {
        "blockchain_tx_hash": result["transaction_hash"],
        "metadata_hash": request.metadata_hash
    })
    
    return BlockchainAnchorResponse(
        success=True,
        scan_id=scan_id,
        transaction_hash=result["transaction_hash"],
        block_number=result.get("block_number"),
        gas_used=result.get("gas_used"),
        timestamp=result["timestamp"]
    )


@app.get("/scans/{scan_id}/verify", response_model=BlockchainVerificationResponse)
async def verify_scan(scan_id: str):
    """Verify a scan's blockchain anchoring."""
    result = await blockchain.verify_anchor(scan_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify anchor"
        )
    
    return BlockchainVerificationResponse(**result)


@app.get("/blockchain/balance")
async def get_wallet_balance():
    """Get the blockchain wallet balance."""
    balance = blockchain.get_balance()
    return {
        "balance_matic": balance,
        "address": blockchain._account.address if blockchain._account else None
    }


# ==================== Email Endpoints ====================

@app.post("/email/send", response_model=EmailResponse)
async def send_email(
    request: EmailRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a custom email."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await email_service.send_template_email(
        to_email=request.to_email,
        template_name=request.template_name,
        template_data=request.template_data
    )
    
    return EmailResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
