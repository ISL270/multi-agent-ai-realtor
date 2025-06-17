"""
Supabase client for the Real Estate AI application.
"""
import os
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client, Client as SupabaseClient

load_dotenv()

class DatabaseClient:
    """A client for interacting with the Supabase database."""
    
    _instance: Optional['DatabaseClient'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Supabase client with environment variables."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
        
        self.client: SupabaseClient = create_client(supabase_url, supabase_key)
    
    def get_properties(self, **filters):
        """
        Retrieve properties based on filters.
        
        Args:
            **filters: Key-value pairs for filtering properties
            
        Returns:
            List of property records matching the filters
        """
        query = self.client.table('properties').select('*', count='exact')
        
        # Apply filters
        for key, value in filters.items():
            if value is not None:
                if key.endswith('_gte'):
                    query = query.gte(key.replace('_gte', ''), value)
                elif key.endswith('_lte'):
                    query = query.lte(key.replace('_lte', ''), value)
                elif key == 'amenities':
                    # Handle amenities filter (many-to-many relationship)
                    query = query.contains('amenities', value)
                else:
                    query = query.eq(key, value)
        
        # Execute the query
        response = query.execute()
        return response.data if hasattr(response, 'data') else []
    
    def get_property_by_id(self, property_id: str):
        """
        Retrieve a single property by its ID with related images and amenities.
        
        Args:
            property_id: The ID of the property to retrieve
            
        Returns:
            Property record with related data or None if not found
        """
        # First get the property
        property_data = self.client.table('properties')\
            .select('*')\
            .eq('id', property_id)\
            .single()\
            .execute()
        
        if not property_data.data:
            return None
            
        # Get property images
        images = self.client.table('property_images')\
            .select('url, is_primary')\
            .eq('property_id', property_id)\
            .execute()
            
        # Get property amenities
        amenities = self.client.table('property_amenities')\
            .select('amenities(name)')\
            .eq('property_id', property_id)\
            .execute()
        
        # Combine the data
        property_data.data['images'] = images.data or []
        property_data.data['amenities'] = [a['amenities']['name'] for a in amenities.data] if amenities.data else []
        
        return property_data.data
