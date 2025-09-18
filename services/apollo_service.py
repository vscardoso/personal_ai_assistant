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
        """Synchronous helper method for the API call"""

        # Split name into first and last name
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Apollo.io People Search API endpoint
        url = f"{self.base_url}/mixed_people/search"

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }

        # Search payload
        payload = {
            "q_person_name": name.strip(),
            "q_organization_name": company.strip(),
            "page": 1,
            "per_page": 1,  # We only need the first match
            "person_titles": [],
            "q_person_locations": [],
            "contact_email_status": ["verified", "guessed", "unavailable"],
        }

        # If we can split first/last name, use more specific search
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name

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

                # Check if we have results
                people = data.get("people", [])
                if not people:
                    logger.info(f"No results found for {name} at {company}")
                    return None

                # Get the first person result
                person = people[0]

                # Extract company information
                organization = person.get("organization", {}) or {}

                result = {
                    "email": person.get("email"),
                    "linkedin_url": person.get("linkedin_url"),
                    "title": person.get("title"),
                    "company_info": {
                        "name": organization.get("name"),
                        "website": organization.get("website_url"),
                        "industry": organization.get("industry"),
                        "size": organization.get("estimated_num_employees"),
                        "location": organization.get("primary_domain")
                    }
                }

                logger.info(f"Found person data for {name}: {result.get('email', 'No email')}")
                return result

            elif response.status_code == 401:
                logger.error("Apollo API authentication failed - check API key")
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

# Create a global instance
apollo_service = ApolloService()