import os
import requests
import logging
from typing import Dict, Optional, Any
import asyncio

logger = logging.getLogger(__name__)

class ApolloService:
    def __init__(self):
        self.api_key = os.getenv("APOLLO_API_KEY")
        self.base_url = "https://api.apollo.io/v1"

        if not self.api_key:
            logger.warning("APOLLO_API_KEY not found in environment variables")

    async def search_person_by_name_company(
        self,
        name: str,
        company: str
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a person by name and company using Apollo.io API

        Args:
            name (str): Full name of the person
            company (str): Company name

        Returns:
            Dict containing email, linkedin_url, title, company_info or None if not found
        """
        if not self.api_key:
            logger.error("Apollo API key not configured")
            return None

        try:
            # Use asyncio to run the synchronous requests call in a thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._search_person_sync, name, company)
            return result

        except Exception as e:
            logger.error(f"Error searching person in Apollo: {e}")
            return None

    def _search_person_sync(self, name: str, company: str) -> Optional[Dict[str, Any]]:
        """Synchronous helper method for the API call using contacts/search endpoint"""

        # Split name into first and last name
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Use Apollo.io Contacts Search API endpoint (available in your plan)
        url = f"{self.base_url}/contacts/search"

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }

        # Search payload for contacts/search
        payload = {
            "page": 1,
            "per_page": 1,  # We only need the first match
            "q_keywords": f"{name} {company}",  # General keyword search
        }

        # Add specific filters if we have them
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if company:
            payload["organization_names"] = [company]

        try:
            logger.info(f"Searching Apollo for: {name} at {company}")

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Check if we have results - contacts API returns different structure
                contacts = data.get("contacts", [])
                if not contacts:
                    logger.info(f"No results found for {name} at {company}")
                    return None

                # Get the first contact result
                contact = contacts[0]

                # Extract company information from contact
                organization = contact.get("organization", {}) or {}

                result = {
                    "email": contact.get("email"),
                    "linkedin_url": contact.get("linkedin_url"),
                    "title": contact.get("title"),
                    "company_info": {
                        "name": organization.get("name"),
                        "website": organization.get("website_url"),
                        "industry": organization.get("industry"),
                        "size": organization.get("estimated_num_employees"),
                        "location": organization.get("primary_domain")
                    }
                }

                logger.info(f"Found contact data for {name}: {result.get('email', 'No email')}")
                return result

            elif response.status_code == 401:
                logger.error("Apollo API authentication failed - check API key")
                return None

            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                if "free plan" in error_data.get("error", "").lower():
                    logger.error("Apollo API requires paid plan for people search")
                else:
                    logger.error("Apollo API access forbidden")
                return None

            elif response.status_code == 429:
                logger.error("Apollo API rate limit exceeded")
                return None

            else:
                logger.error(f"Apollo API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when calling Apollo API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Apollo API call: {e}")
            return None

    async def enrich_prospect_data(
        self,
        name: str,
        company: str
    ) -> Dict[str, Any]:
        """
        Enrich prospect data with Apollo.io information

        Args:
            name (str): Person's full name
            company (str): Company name

        Returns:
            Dict with enriched data including basic_info populated
        """
        apollo_data = await self.search_person_by_name_company(name, company)

        if not apollo_data:
            return {
                "basic_info": {
                    "data_source": "apollo",
                    "enriched": False,
                    "error": "No data found"
                }
            }

        # Structure the data for our prospect model
        enriched_data = {
            "basic_info": {
                "data_source": "apollo",
                "enriched": True,
                "email": apollo_data.get("email"),
                "linkedin_url": apollo_data.get("linkedin_url"),
                "title": apollo_data.get("title"),
                "company": {
                    "name": apollo_data.get("company_info", {}).get("name"),
                    "website": apollo_data.get("company_info", {}).get("website"),
                    "industry": apollo_data.get("company_info", {}).get("industry"),
                    "size": apollo_data.get("company_info", {}).get("size")
                }
            }
        }

        return enriched_data

    async def search_organization(self, company: str) -> Optional[Dict[str, Any]]:
        """
        Search for organization information using Apollo.io organizations/search

        Args:
            company (str): Company name

        Returns:
            Dict with organization data or None if not found
        """
        if not self.api_key:
            logger.error("Apollo API key not configured")
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._search_organization_sync, company)
            return result

        except Exception as e:
            logger.error(f"Error searching organization in Apollo: {e}")
            return None

    def _search_organization_sync(self, company: str) -> Optional[Dict[str, Any]]:
        """Search for organization using organizations/search endpoint"""

        url = f"{self.base_url}/organizations/search"

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }

        payload = {
            "q_organization_name": company.strip(),
            "page": 1,
            "per_page": 1
        }

        try:
            logger.info(f"Searching Apollo for organization: {company}")

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                organizations = data.get("organizations", [])

                if not organizations:
                    logger.info(f"No organization found for {company}")
                    return None

                org = organizations[0]

                result = {
                    "name": org.get("name"),
                    "website": org.get("website_url"),
                    "industry": org.get("industry"),
                    "size": org.get("estimated_num_employees"),
                    "description": org.get("short_description"),
                    "linkedin_url": org.get("linkedin_url"),
                    "location": org.get("primary_location", {}).get("city")
                }

                logger.info(f"Found organization data for {company}")
                return result

            else:
                logger.error(f"Apollo organizations API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error in organization search: {e}")
            return None

# Create a global instance
apollo_service = ApolloService()