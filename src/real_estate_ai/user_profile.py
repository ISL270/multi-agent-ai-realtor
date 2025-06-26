from typing import Optional

from pydantic import BaseModel, Field


# Define profile structure
class UserProfile(BaseModel):
    """Represents the full representation of a user.

    This model stores the user's basic information,
    such as name, job, number of children, and current living location.
    It also stores the user's property preferences.
    """

    name: Optional[str] = None
    job: Optional[str] = None
    num_of_children: Optional[int] = None
    city_of_residence: Optional[str] = None
    property_preferences: Optional[str] = Field(
        None, description="A summery string containing the user's property preferences"
    )
