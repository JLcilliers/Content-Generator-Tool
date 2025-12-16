"""
Client Profile Management System
Handles creating, reading, updating, and deleting client profiles.
"""

import json
import os
from typing import Dict, List, Optional


class ClientManager:
    """Manages client profiles stored as JSON files."""
    
    def __init__(self, clients_dir: str = "clients"):
        self.clients_dir = clients_dir
        os.makedirs(clients_dir, exist_ok=True)
    
    def create_client(self, client_name: str, client_data: Dict) -> bool:
        """Create a new client profile."""
        client_file = self._get_client_file(client_name)
        
        if os.path.exists(client_file):
            print(f"Client '{client_name}' already exists.")
            return False
        
        # Set default structure if not provided
        default_structure = {
            "client_name": client_name,
            "site": "",
            "information": [],
            "restrictions": {
                "legal": [],
                "brand": [],
                "seo": [],
                "content_integrity": []
            },
            "requirements": {
                "word_count": "",
                "readability_score": "",
                "tone": "",
                "mandatory_mentions": [],
                "schema_required": False,
                "images_required": 0,
                "cta_required": True,
                "internal_links_min": 6
            }
        }
        
        # Merge provided data with defaults
        merged_data = {**default_structure, **client_data}
        merged_data["client_name"] = client_name
        
        with open(client_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        print(f"Client '{client_name}' created successfully.")
        return True
    
    def get_client(self, client_name: str) -> Optional[Dict]:
        """Retrieve a client profile."""
        client_file = self._get_client_file(client_name)
        
        if not os.path.exists(client_file):
            print(f"Client '{client_name}' not found.")
            return None
        
        with open(client_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_client(self, client_name: str, updates: Dict) -> bool:
        """Update an existing client profile."""
        client_data = self.get_client(client_name)
        
        if not client_data:
            return False
        
        # Deep merge for nested dictionaries
        for key, value in updates.items():
            if isinstance(value, dict) and key in client_data:
                client_data[key].update(value)
            else:
                client_data[key] = value
        
        client_file = self._get_client_file(client_name)
        with open(client_file, 'w', encoding='utf-8') as f:
            json.dump(client_data, f, indent=2, ensure_ascii=False)
        
        print(f"Client '{client_name}' updated successfully.")
        return True
    
    def delete_client(self, client_name: str) -> bool:
        """Delete a client profile."""
        client_file = self._get_client_file(client_name)
        
        if not os.path.exists(client_file):
            print(f"Client '{client_name}' not found.")
            return False
        
        os.remove(client_file)
        print(f"Client '{client_name}' deleted successfully.")
        return True
    
    def list_clients(self) -> List[str]:
        """List all client names."""
        if not os.path.exists(self.clients_dir):
            return []
        
        clients = []
        for file in os.listdir(self.clients_dir):
            if file.endswith('.json'):
                clients.append(file[:-5])  # Remove .json extension
        
        return sorted(clients)
    
    def _get_client_file(self, client_name: str) -> str:
        """Get the file path for a client."""
        safe_name = client_name.replace(' ', '_').lower()
        return os.path.join(self.clients_dir, f"{safe_name}.json")
