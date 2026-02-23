"""
Test suite for DepoSafety V2 API.
Run with: pytest test_api.py -v
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ==================== Health Tests ====================

def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert "services" in data


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ==================== Authentication Tests ====================

def test_register_validation():
    """Test registration validation."""
    # Invalid email
    response = client.post("/auth/register", json={
        "email": "invalid-email",
        "password": "short",
        "full_name": "Test User"
    })
    assert response.status_code == 422


def test_login_validation():
    """Test login validation."""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


# ==================== Model Tests ====================

def test_user_models():
    """Test user Pydantic models."""
    from models import UserCreate, UserRole
    
    user = UserCreate(
        email="test@example.com",
        password="securepassword123",
        full_name="Test User",
        role=UserRole.INSPECTOR
    )
    assert user.email == "test@example.com"
    assert user.role == UserRole.INSPECTOR


def test_property_models():
    """Test property Pydantic models."""
    from models import PropertyCreate, PropertyType
    
    prop = PropertyCreate(
        name="Test Property",
        address="123 Test St",
        city="Test City",
        state="CA",
        zip_code="12345",
        property_type=PropertyType.APARTMENT
    )
    assert prop.name == "Test Property"
    assert prop.property_type == PropertyType.APARTMENT


def test_scan_models():
    """Test scan Pydantic models."""
    from models import ScanCreate, InspectionType, ScanStatus
    from uuid import uuid4
    
    scan = ScanCreate(
        property_id=uuid4(),
        inspection_type=InspectionType.MOVE_IN,
        notes="Test inspection"
    )
    assert scan.inspection_type == InspectionType.MOVE_IN


# ==================== Webhook Tests ====================

def test_webhook_payload():
    """Test webhook payload model."""
    from models import ProcessingWebhookPayload, ScanStatus
    
    payload = ProcessingWebhookPayload(
        scan_id="test-scan-id",
        status=ScanStatus.COMPLETED,
        model_3d_url="https://example.com/model.glb"
    )
    assert payload.status == ScanStatus.COMPLETED
    assert payload.model_3d_url is not None


# ==================== Blockchain Tests ====================

def test_blockchain_anchor_request():
    """Test blockchain anchor request model."""
    from models import BlockchainAnchorRequest
    from uuid import uuid4
    
    request = BlockchainAnchorRequest(
        scan_id=uuid4(),
        metadata_hash="0x1234567890abcdef"
    )
    assert request.metadata_hash.startswith("0x")


def test_blockchain_client_initialization():
    """Test blockchain client initialization."""
    from blockchain import blockchain
    
    # Should be initialized (may be disconnected if no config)
    assert blockchain is not None


# ==================== Storage Tests ====================

def test_storage_key_generation():
    """Test video key generation."""
    from storage import storage
    
    key = storage.generate_video_key("scan-123", "my video.mp4")
    assert key.startswith("scans/scan-123/")
    assert key.endswith(".mp4")
    assert "my_video" in key


# ==================== Email Tests ====================

def test_email_templates():
    """Test email templates exist."""
    from email_service import email_service
    
    assert "scan_completed" in email_service.TEMPLATES
    assert "welcome" in email_service.TEMPLATES
    assert "password_reset" in email_service.TEMPLATES


# ==================== Auth Tests ====================

def test_password_hashing():
    """Test password hashing utilities."""
    from auth import get_password_hash, verify_password
    
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_token_creation():
    """Test JWT token creation."""
    from auth import create_access_token, decode_token
    
    data = {"sub": "user-123", "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    decoded = decode_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "test@example.com"


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_database_client():
    """Test database client initialization."""
    from database import db
    
    assert db is not None
    # Client may be None if no credentials configured


@pytest.mark.asyncio
async def test_storage_client():
    """Test storage client initialization."""
    from storage import storage
    
    assert storage is not None
    assert storage.bucket_name == "deposafety-videos"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
