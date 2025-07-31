from typing import List, Optional

from pydantic import BaseModel


class Property(BaseModel):
    """
    Represents a single property listing with a single, required image URL.
    All fields are strictly typed for maximum type safety.
    """

    id: str
    title: str
    description: Optional[str]
    price: float
    property_type: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    city: Optional[str]
    area_sqm: Optional[float]
    image_url: str  # Non-optional. Always a valid image URL for this property.
    amenities: List[str] = []
