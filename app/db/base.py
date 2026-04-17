"""Database base configuration for SentinelGuard."""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, String, Text, Boolean, Integer, BigInteger, Column
from sqlalchemy.dialects.postgresql import INET, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func


Base = declarative_base()


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            server_default=func.now()
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now()
        )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    @declared_attr
    def is_deleted(cls):
        return Column(
            Boolean,
            nullable=False,
            default=False,
            server_default='false'
        )
    
    @declared_attr
    def deleted_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=True
        )


class BaseModel(Base, TimestampMixin):
    """Base model class with common fields."""
    
    __abstract__ = True
    
    id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        autoincrement=True
    )
    
    def to_dict(self, exclude: set[str] = None) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        exclude = exclude or set()
        
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                
                # Handle datetime serialization
                if isinstance(value, datetime):
                    value = value.isoformat()
                # Handle INET type
                elif hasattr(value, 'addr'):  # PostgreSQL INET type
                    value = str(value)
                # Handle arrays
                elif isinstance(value, list):
                    value = list(value)
                
                result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id})>"


# Import Column from sqlalchemy for the mixins
from sqlalchemy import Column
