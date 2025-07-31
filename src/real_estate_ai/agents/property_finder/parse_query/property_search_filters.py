import logging
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class PropertySearchFilters(BaseModel):
    """
    Pydantic model for structured property search filters.
    Matches the database schema and provides flexible search capabilities.
    """

    # Sorting
    sort_by: Optional[str] = Field(None, description="Field to sort by. Allowed: 'price', 'area'.")
    sort_order: Optional[str] = Field(None, description="Sort order. Allowed: 'asc' (ascending), 'desc' (descending).")

    # Price range
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")

    # Property details
    city: Optional[str] = Field(None, description="Filter by city name")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    property_type: Optional[str] = Field(None, description="Type of property (e.g., apartment, villa, townhouse)")
    amenities: Optional[List[str]] = Field(None, description="List of amenity names to filter by")

    # Area in square meters
    min_area: Optional[float] = Field(None, ge=0, description="Minimum area in square meters")
    max_area: Optional[float] = Field(None, ge=0, description="Maximum area in square meters")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        if v is None:
            return v
        allowed = {"price", "area"}
        if v not in allowed:
            logger.warning("sort_by value '%s' is invalid, must be one of %s. Ignoring.", v, allowed)
            return None
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v is None:
            return v
        allowed = {"asc", "desc"}
        if v not in allowed:
            logger.warning("sort_order value '%s' is invalid, must be one of %s. Ignoring.", v, allowed)
            return None
        return v

    @field_validator("amenities", mode="before")
    @classmethod
    def empty_amenities_to_none(cls, v):
        """Convert empty list to None for amenities."""
        if v == []:
            return None
        return v

    @model_validator(mode="after")
    def validate_price_range(self):
        """Log a warning if min_price is greater than max_price."""
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                logger.warning(
                    "min_price (%s) is greater than max_price (%s), this may return no results",
                    self.min_price,
                    self.max_price,
                )
        return self

    @model_validator(mode="after")
    def validate_area_range(self):
        """Log a warning if min_area is greater than max_area."""
        if self.min_area is not None and self.max_area is not None:
            if self.min_area > self.max_area:
                logger.warning(
                    "min_area (%s) is greater than max_area (%s), this may return no results",
                    self.min_area,
                    self.max_area,
                )
        return self
