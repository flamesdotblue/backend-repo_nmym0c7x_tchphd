"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (you may keep or remove if unused):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Blog schema used by the app
class BlogPost(BaseModel):
    """
    Blog posts collection schema
    Collection name: "blogpost" (lowercase of class name)
    """
    title: str = Field(..., min_length=1, max_length=160, description="Post title")
    content: str = Field(..., min_length=1, description="Main content (markdown or plain text)")
    author: str = Field(..., min_length=1, max_length=60, description="Author name")
    tags: Optional[List[str]] = Field(default=None, description="List of tags")
