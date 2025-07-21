from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models to handle MongoDB's ObjectId."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    """Base model for all MongoDB documents with common fields and configuration."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict method to convert _id to string."""
        dict_repr = super().dict(**kwargs)
        # Convert _id to string if it exists
        if "_id" in dict_repr and dict_repr["_id"] is not None:
            dict_repr["_id"] = str(dict_repr["_id"])
        return dict_repr


class TimestampedModel(MongoBaseModel):
    """Base model with timestamp fields for created and updated times."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {**MongoBaseModel.Config.json_encoders, datetime: lambda v: v.isoformat()}


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    
    skip: int = Field(0, ge=0)
    limit: int = Field(10, gt=0, le=100)
    
    @classmethod
    def from_page(cls, page: int = 1, page_size: int = 10):
        """Create pagination params from page number and page size."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100
        
        return cls(
            skip=(page - 1) * page_size,
            limit=page_size
        )
