"""
Pydantic models for DepoSafety V2 API.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, UUID4


# ==================== Enums ====================

class UserRole(str, Enum):
    ADMIN = "admin"
    INSPECTOR = "inspector"
    LANDLORD = "landlord"
    TENANT = "tenant"


class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    COMMERCIAL = "commercial"
    STORAGE = "storage"


class ScanStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InspectionType(str, Enum):
    MOVE_IN = "move_in"
    MOVE_OUT = "move_out"
    ROUTINE = "routine"
    DAMAGE = "damage"


# ==================== User Models ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.TENANT
    phone: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== Property Models ====================

class PropertyBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    property_type: PropertyType = PropertyType.APARTMENT
    description: Optional[str] = None
    square_feet: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None


class PropertyCreate(PropertyBase):
    owner_id: Optional[UUID4] = None


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    property_type: Optional[PropertyType] = None
    description: Optional[str] = None
    square_feet: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None


class PropertyResponse(PropertyBase):
    id: UUID4
    owner_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    scan_count: int = 0
    
    class Config:
        from_attributes = True


# ==================== Scan Models ====================

class ScanBase(BaseModel):
    property_id: UUID4
    inspection_type: InspectionType
    notes: Optional[str] = None


class ScanCreate(ScanBase):
    pass


class ScanUpdate(BaseModel):
    status: Optional[ScanStatus] = None
    notes: Optional[str] = None
    video_url: Optional[str] = None
    model_3d_url: Optional[str] = None
    blockchain_tx_hash: Optional[str] = None


class ScanResponse(ScanBase):
    id: UUID4
    inspector_id: UUID4
    status: ScanStatus
    video_url: Optional[str] = None
    model_3d_url: Optional[str] = None
    blockchain_tx_hash: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScanDetailResponse(ScanResponse):
    property: Optional[PropertyResponse] = None
    inspector: Optional[UserResponse] = None


class ScanListResponse(BaseModel):
    total: int
    scans: List[ScanResponse]


# ==================== Video Upload Models ====================

class VideoUploadRequest(BaseModel):
    scan_id: UUID4
    filename: str
    content_type: str = "video/mp4"
    file_size: int


class VideoUploadResponse(BaseModel):
    upload_url: str
    scan_id: UUID4
    expires_in: int = 3600


class VideoUploadComplete(BaseModel):
    scan_id: UUID4
    video_key: str
    video_url: str


# ==================== Webhook Models ====================

class ProcessingWebhookPayload(BaseModel):
    scan_id: str
    status: ScanStatus
    model_3d_url: Optional[str] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ProcessingWebhookResponse(BaseModel):
    success: bool
    message: str
    scan_id: str


# ==================== Blockchain Models ====================

class BlockchainAnchorRequest(BaseModel):
    scan_id: UUID4
    metadata_hash: str  # IPFS or content hash


class BlockchainAnchorResponse(BaseModel):
    success: bool
    scan_id: UUID4
    transaction_hash: str
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    timestamp: datetime


class BlockchainVerificationResponse(BaseModel):
    scan_id: UUID4
    is_verified: bool
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    metadata_hash: Optional[str] = None


# ==================== Email Models ====================

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    template_name: str
    template_data: Dict[str, Any] = Field(default_factory=dict)


class EmailResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


# ==================== Health & Misc ====================

class HealthResponse(BaseModel):
    status: str
    version: str = "2.0.0"
    timestamp: datetime
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
