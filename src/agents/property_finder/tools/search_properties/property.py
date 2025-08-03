from typing import List, Optional
from pydantic import BaseModel

class Property(BaseModel):
    id: str
    title: str
    description: Optional[str]
    price: float
    property_type: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    city: Optional[str]
    area_sqm: Optional[float]
    image_url: str
    amenities: List[str] = []
