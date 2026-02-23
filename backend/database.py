"""
Supabase PostgreSQL database client configuration.
"""
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Supabase database client wrapper."""
    
    _instance: Optional['DatabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            settings = get_settings()
            if settings.supabase_url and settings.supabase_key:
                self._client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )
            else:
                logger.warning("Supabase credentials not configured")
    
    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client instance."""
        return self._client
    
    # ==================== User Operations ====================
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user in the database."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("users").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("users").select("*").eq("email", email).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("users").update(user_data).eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if not self._client:
            return False
        
        try:
            self._client.table("users").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all users with pagination."""
        if not self._client:
            return []
        
        try:
            response = self._client.table("users").select("*").range(offset, offset + limit - 1).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
    
    # ==================== Property Operations ====================
    
    async def create_property(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new property."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("properties").insert(property_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating property: {e}")
            return None
    
    async def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get property by ID."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("properties").select("*").eq("id", property_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting property: {e}")
            return None
    
    async def update_property(self, property_id: str, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update property data."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("properties").update(property_data).eq("id", property_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating property: {e}")
            return None
    
    async def delete_property(self, property_id: str) -> bool:
        """Delete a property."""
        if not self._client:
            return False
        
        try:
            self._client.table("properties").delete().eq("id", property_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting property: {e}")
            return False
    
    async def list_properties(
        self, 
        owner_id: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List properties with optional owner filter."""
        if not self._client:
            return []
        
        try:
            query = self._client.table("properties").select("*")
            if owner_id:
                query = query.eq("owner_id", owner_id)
            response = query.range(offset, offset + limit - 1).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing properties: {e}")
            return []
    
    # ==================== Scan Operations ====================
    
    async def create_scan(self, scan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new scan record."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("scans").insert(scan_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating scan: {e}")
            return None
    
    async def get_scan_by_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan by ID."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("scans").select("*").eq("id", scan_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting scan: {e}")
            return None
    
    async def get_scan_with_details(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan with property and inspector details."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("scans").select(
                "*, properties(*), users:inspector_id(*)"
            ).eq("id", scan_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting scan details: {e}")
            return None
    
    async def update_scan(self, scan_id: str, scan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update scan data."""
        if not self._client:
            return None
        
        try:
            response = self._client.table("scans").update(scan_data).eq("id", scan_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating scan: {e}")
            return None
    
    async def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan."""
        if not self._client:
            return False
        
        try:
            self._client.table("scans").delete().eq("id", scan_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting scan: {e}")
            return False
    
    async def list_scans(
        self,
        property_id: Optional[str] = None,
        inspector_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List scans with optional filters."""
        if not self._client:
            return []
        
        try:
            query = self._client.table("scans").select("*")
            if property_id:
                query = query.eq("property_id", property_id)
            if inspector_id:
                query = query.eq("inspector_id", inspector_id)
            if status:
                query = query.eq("status", status)
            response = query.range(offset, offset + limit - 1).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing scans: {e}")
            return []
    
    async def count_scans(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count scans with optional filters."""
        if not self._client:
            return 0
        
        try:
            query = self._client.table("scans").select("id", count="exact")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error counting scans: {e}")
            return 0


# Global database client instance
db = DatabaseClient()
