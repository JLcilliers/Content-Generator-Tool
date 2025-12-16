"""
Content Brief Creator - Main Interface
Interactive CLI for creating content briefs using client profiles.
"""

import sys
from typing import List
from client_manager import ClientManager
from brief_generator import BriefGenerator
from document_formatter import DocumentFormatter
from ai_provider import AIProvider


class ContentBriefCreator:
    """Main application interface for content brief creation."""
    
    def __init__(self):
        self.client_manager = ClientManager()
        self.doc_formatter = DocumentFormatter()
        
        # Check for available AI providers
        available_providers = AIProvider.list_available_providers()
        if not available_providers:
            print("Error: No AI provider API keys found.")
            print("\nPlease set up at least one AI provider API key:")
            print("1. Copy .env.example to .env")
            print("2. Add API keys for OpenAI, Claude, Perplexity, or Mistral to .env")
            sys.exit(1)
    
    def run(self):
        """Run the main application loop."""
        print("\n" + "="*60)
        print("Content Brief Creator")
        print("="*60)
        
        while True:
            print("\nMain Menu:")
            print("1. Create Brief")
            print("2. Manage Clients")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                self.create_brief_workflow()
            elif choice == "2":
                self.manage_clients_workflow()
            elif choice == "3":
                print("\nExiting...")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def create_brief_workflow(self):
        """Workflow for creating a new content brief."""
        print("\n" + "-"*60)
        print("Create Content Brief")
        print("-"*60)
        
        # Select AI provider
        available_providers = AIProvider.list_available_providers()
        print("\nAvailable AI providers:")
        for idx, provider in enumerate(available_providers, 1):
            print(f"{idx}. {provider.upper()}")
        
        try:
            provider_idx = int(input("\nSelect AI provider (or press Enter for default): ").strip() or "1") - 1
            if provider_idx < 0 or provider_idx >= len(available_providers):
                print("Invalid selection. Using default provider.")
                selected_provider = available_providers[0]
            else:
                selected_provider = available_providers[provider_idx]
        except ValueError:
            print("Invalid input. Using default provider.")
            selected_provider = available_providers[0]
        
        print(f"Using AI provider: {selected_provider.upper()}")
        
        # Initialize brief generator with selected provider
        try:
            brief_generator = BriefGenerator(provider=selected_provider)
        except ValueError as e:
            print(f"Error initializing AI provider: {e}")
            return
        
        # List available clients
        clients = self.client_manager.list_clients()
        
        if not clients:
            print("\nNo clients found. Please create a client first.")
            return
        
        print("\nAvailable clients:")
        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client}")
        
        # Select client
        try:
            client_idx = int(input("\nSelect client number: ").strip()) - 1
            if client_idx < 0 or client_idx >= len(clients):
                print("Invalid selection.")
                return
            
            selected_client = clients[client_idx]
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        # Get client data
        client_data = self.client_manager.get_client(selected_client)
        if not client_data:
            return
        
        print(f"\nClient: {client_data['client_name']}")
        print(f"Site: {client_data['site']}")
        
        # Get topic and keywords
        print("\nBrief Details:")
        topic = input("Topic: ").strip()
        if not topic:
            print("Topic is required.")
            return
        
        primary_kw = input("Primary keyword: ").strip()
        if not primary_kw:
            print("Primary keyword is required.")
            return
        
        secondary_kws_input = input("Secondary keywords (comma-separated): ").strip()
        secondary_kws = [kw.strip() for kw in secondary_kws_input.split(',') if kw.strip()]
        
        if not secondary_kws:
            print("At least one secondary keyword is required.")
            return
        
        # Generate brief
        print("\n" + "="*60)
        print(f"Generating content brief with {selected_provider.upper()}...")
        print("="*60)
        
        try:
            brief_data = brief_generator.generate_brief(
                client_data=client_data,
                topic=topic,
                primary_kw=primary_kw,
                secondary_kws=secondary_kws
            )
            
            print("\nBrief generated successfully!")
            
            # Create document
            print("\nCreating Word document...")
            filepath = self.doc_formatter.create_brief_document(brief_data)
            
            print(f"\n✓ Brief created successfully!")
            print(f"File saved to: {filepath}")
            
        except Exception as e:
            print(f"\nError generating brief: {e}")
            import traceback
            traceback.print_exc()
    
    def manage_clients_workflow(self):
        """Workflow for managing client profiles."""
        print("\n" + "-"*60)
        print("Manage Clients")
        print("-"*60)
        
        while True:
            print("\nClient Management:")
            print("1. List Clients")
            print("2. Create Client")
            print("3. View Client")
            print("4. Update Client")
            print("5. Delete Client")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == "1":
                self.list_clients()
            elif choice == "2":
                self.create_client()
            elif choice == "3":
                self.view_client()
            elif choice == "4":
                self.update_client()
            elif choice == "5":
                self.delete_client()
            elif choice == "6":
                break
            else:
                print("Invalid choice.")
    
    def list_clients(self):
        """List all clients."""
        clients = self.client_manager.list_clients()
        
        if not clients:
            print("\nNo clients found.")
            return
        
        print("\nClients:")
        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client}")
    
    def create_client(self):
        """Create a new client."""
        print("\n" + "-"*40)
        print("Create New Client")
        print("-"*40)
        
        client_name = input("Client name: ").strip()
        if not client_name:
            print("Client name is required.")
            return
        
        site = input("Website URL: ").strip()
        
        print("\nRestrictions:")
        legal = self._get_list_input("Legal restrictions")
        brand = self._get_list_input("Brand restrictions")
        seo = self._get_list_input("SEO restrictions")
        content = self._get_list_input("Content integrity restrictions")
        
        print("\nRequirements:")
        word_count = input("Word count range (e.g., 800-1200): ").strip()
        tone = input("Tone (e.g., Professional, friendly): ").strip()
        mandatory = self._get_list_input("Mandatory mentions")
        
        client_data = {
            "site": site,
            "restrictions": {
                "legal": legal,
                "brand": brand,
                "seo": seo,
                "content_integrity": content
            },
            "requirements": {
                "word_count": word_count,
                "readability_score": "8th grade level",
                "tone": tone,
                "mandatory_mentions": mandatory,
                "schema_required": True,
                "images_required": 2,
                "cta_required": True,
                "internal_links_min": 6
            }
        }
        
        self.client_manager.create_client(client_name, client_data)
    
    def view_client(self):
        """View a client's details."""
        clients = self.client_manager.list_clients()
        
        if not clients:
            print("\nNo clients found.")
            return
        
        print("\nAvailable clients:")
        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client}")
        
        try:
            client_idx = int(input("\nSelect client number: ").strip()) - 1
            if client_idx < 0 or client_idx >= len(clients):
                print("Invalid selection.")
                return
            
            selected_client = clients[client_idx]
            client_data = self.client_manager.get_client(selected_client)
            
            if client_data:
                import json
                print("\n" + json.dumps(client_data, indent=2))
        
        except ValueError:
            print("Invalid input.")
    
    def update_client(self):
        """Update a client's information."""
        print("\nUpdate functionality coming soon.")
        print("You can manually edit the JSON files in the 'clients' folder.")
    
    def delete_client(self):
        """Delete a client."""
        clients = self.client_manager.list_clients()
        
        if not clients:
            print("\nNo clients found.")
            return
        
        print("\nAvailable clients:")
        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client}")
        
        try:
            client_idx = int(input("\nSelect client number to delete: ").strip()) - 1
            if client_idx < 0 or client_idx >= len(clients):
                print("Invalid selection.")
                return
            
            selected_client = clients[client_idx]
            
            confirm = input(f"\nAre you sure you want to delete '{selected_client}'? (yes/no): ").strip().lower()
            if confirm == "yes":
                self.client_manager.delete_client(selected_client)
        
        except ValueError:
            print("Invalid input.")
    
    def _get_list_input(self, prompt: str) -> List[str]:
        """Get a list of items from user input."""
        print(f"\n{prompt} (enter items one per line, empty line to finish):")
        items = []
        while True:
            item = input("  - ").strip()
            if not item:
                break
            items.append(item)
        return items


def main():
    """Entry point for the application."""
    app = ContentBriefCreator()
    app.run()


if __name__ == "__main__":
    main()
