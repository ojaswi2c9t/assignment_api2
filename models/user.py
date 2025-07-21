from typing import List, Optional
from datetime import datetime
from pydantic import Field, EmailStr, validator
from models.base import TimestampedModel


class Address(TimestampedModel):
    """User address model."""
    
    full_name: str = Field(...)
    address_line1: str = Field(...)
    address_line2: Optional[str] = None
    city: str = Field(...)
    state: str = Field(...)
    postal_code: str = Field(...)
    country: str = Field(...)
    phone: Optional[str] = None
    is_default: bool = Field(default=False)


class User(TimestampedModel):
    """User model as stored in MongoDB."""
    
    email: EmailStr = Field(...)
    password_hash: str = Field(...)  # Hashed password, never store plain passwords
    first_name: str = Field(...)
    last_name: str = Field(...)
    addresses: List[Address] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    last_login: Optional[datetime] = None
    
    @validator('email')
    def email_lowercase(cls, v):
        """Convert email to lowercase."""
        return v.lower() if v else v
    
    @classmethod
    async def get_by_id(cls, db, user_id):
        """Get user by ID."""
        from bson import ObjectId
        from core.database import get_collection
        
        if not ObjectId.is_valid(user_id):
            return None
            
        user_data = await get_collection("users").find_one({"_id": ObjectId(user_id)})
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    async def get_by_email(cls, db, email):
        """Get user by email."""
        from core.database import get_collection
        
        user_data = await get_collection("users").find_one({"email": email.lower()})
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    async def create(cls, db, user_data):
        """Create a new user."""
        from core.database import get_collection
        
        # Check if email already exists
        existing = await cls.get_by_email(db, user_data["email"])
        if existing:
            raise ValueError("Email already registered")
        
        user = cls(**user_data)
        result = await get_collection("users").insert_one(user.dict(by_alias=True))
        user.id = result.inserted_id
        return user
    
    @classmethod
    async def update(cls, db, user_id, user_data):
        """Update an existing user."""
        from bson import ObjectId
        from core.database import get_collection
        
        if not ObjectId.is_valid(user_id):
            return None
            
        user_data["updated_at"] = datetime.utcnow()
        await get_collection("users").update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_data}
        )
        return await cls.get_by_id(db, user_id)
    
    def has_default_address(self) -> bool:
        """Check if user has a default address."""
        return any(addr.is_default for addr in self.addresses)
    
    def get_default_address(self) -> Optional[Address]:
        """Get user's default address."""
        for addr in self.addresses:
            if addr.is_default:
                return addr
        return None if not self.addresses else self.addresses[0] 