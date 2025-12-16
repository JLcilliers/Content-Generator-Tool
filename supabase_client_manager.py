"""
Supabase Client Profile Management System
Handles creating, reading, updating, and deleting client profiles using Supabase.
"""

import os
from typing import Dict, List, Optional

# Try to import streamlit for secrets support
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from supabase import create_client, Client


def get_config(key: str, default: str = None) -> Optional[str]:
    """Get configuration from environment or Streamlit secrets."""
    # Try environment variable first
    value = os.getenv(key)
    if value:
        return value

    # Try Streamlit secrets if available
    if STREAMLIT_AVAILABLE:
        try:
            return st.secrets.get(key, default)
        except (FileNotFoundError, KeyError, AttributeError):
            pass

    return default


class SupabaseClientManager:
    """Manages client profiles stored in Supabase database."""

    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = get_config('SUPABASE_URL')
        supabase_key = get_config('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables or Streamlit secrets")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = 'clients'

    def create_client(self, client_name: str, client_data: Dict) -> bool:
        """Create a new client profile in Supabase."""
        try:
            # Check if client already exists
            existing = self.get_client(client_name)
            if existing:
                return False

            # Set default structure if not provided
            default_structure = {
                "client_name": client_name,
                "site": "",
                "industry": "",
                "target_audience": "",
                "brand_voice": "",
                "content_goals": "",
                "restrictions": {
                    "legal": [],
                    "brand": [],
                    "seo": [],
                    "content_integrity": []
                },
                "requirements": {
                    "word_count": None,
                    "readability_score": "",
                    "tone": "",
                    "mandatory_mentions": [],
                    "schema_required": False,
                    "images_required": 0,
                    "cta_required": True,
                    "internal_links_min": 3
                }
            }

            # Merge provided data with defaults
            merged_data = {**default_structure, **client_data}
            merged_data["client_name"] = client_name

            # Insert into Supabase
            response = self.client.table(self.table_name).insert(merged_data).execute()

            return bool(response.data)

        except Exception as e:
            print(f"Error creating client '{client_name}': {str(e)}")
            return False

    def get_client(self, client_name: str) -> Optional[Dict]:
        """Retrieve a client profile from Supabase."""
        try:
            response = self.client.table(self.table_name).select("*").eq("client_name", client_name).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]

            return None

        except Exception as e:
            print(f"Error retrieving client '{client_name}': {str(e)}")
            return None

    def update_client(self, client_name: str, updates: Dict) -> bool:
        """Update an existing client profile in Supabase."""
        try:
            # Get existing client data
            client_data = self.get_client(client_name)

            if not client_data:
                return False

            # Deep merge for nested dictionaries
            for key, value in updates.items():
                if isinstance(value, dict) and key in client_data:
                    if isinstance(client_data[key], dict):
                        client_data[key].update(value)
                    else:
                        client_data[key] = value
                else:
                    client_data[key] = value

            # Remove id and created_at fields if present (they shouldn't be updated)
            client_data.pop('id', None)
            client_data.pop('created_at', None)
            client_data.pop('updated_at', None)

            # Update in Supabase
            response = self.client.table(self.table_name).update(client_data).eq("client_name", client_name).execute()

            return bool(response.data)

        except Exception as e:
            print(f"Error updating client '{client_name}': {str(e)}")
            return False

    def delete_client(self, client_name: str) -> bool:
        """Delete a client profile from Supabase."""
        try:
            response = self.client.table(self.table_name).delete().eq("client_name", client_name).execute()
            return bool(response.data)

        except Exception as e:
            print(f"Error deleting client '{client_name}': {str(e)}")
            return False

    def list_clients(self) -> List[str]:
        """List all client names from Supabase."""
        try:
            response = self.client.table(self.table_name).select("client_name").execute()

            if response.data:
                return sorted([client['client_name'] for client in response.data])
            return []

        except Exception as e:
            print(f"Error listing clients: {str(e)}")
            return []

    def get_all_clients(self) -> List[Dict]:
        """Get all client profiles from Supabase."""
        try:
            response = self.client.table(self.table_name).select("*").execute()

            if response.data:
                return response.data
            return []

        except Exception as e:
            print(f"Error getting all clients: {str(e)}")
            return []

    def client_exists(self, client_name: str) -> bool:
        """Check if a client exists in Supabase."""
        return self.get_client(client_name) is not None
