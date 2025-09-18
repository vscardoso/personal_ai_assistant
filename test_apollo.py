#!/usr/bin/env python3
"""
Test script for Apollo.io API integration
Tests the apollo_service with real API calls

Usage:
    python test_apollo.py

Environment Variables Required:
    APOLLO_API_KEY - Your Apollo.io API key

Example:
    export APOLLO_API_KEY=your-api-key-here
    python test_apollo.py
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add the current directory to Python path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.apollo_service import apollo_service
except ImportError as e:
    print(f"❌ Error importing apollo_service: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)

# Configure logging for debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_header(title: str) -> None:
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_json(data: Any, title: str = "Result") -> None:
    """Print data as formatted JSON"""
    print(f"\n{title}:")
    print("-" * 40)
    try:
        if data is None:
            print("null")
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error formatting JSON: {e}")
        print(str(data))

async def test_person_search(name: str, company: str) -> Optional[Dict[str, Any]]:
    """
    Test Apollo.io person search functionality

    Args:
        name: Full name of the person
        company: Company name

    Returns:
        Search result or None if failed
    """
    print(f"\nSearching for: {name} at {company}")

    try:
        # Test the search function
        result = await apollo_service.search_person_by_name_company(name, company)

        if result:
            logger.info(f"Found person data for {name}")
            print_json(result, f"Person Data for {name}")

            # Validate the result structure
            expected_keys = ["email", "linkedin_url", "title", "company_info"]
            missing_keys = [key for key in expected_keys if key not in result]

            if missing_keys:
                logger.warning(f"Missing keys in result: {missing_keys}")
            else:
                logger.info("Result structure is valid")

        else:
            logger.warning(f"No data found for {name} at {company}")
            print(f"No results found for {name} at {company}")

        return result

    except Exception as e:
        logger.error(f"Error searching for {name}: {e}")
        print(f"Search failed: {str(e)}")
        return None

async def test_prospect_enrichment(name: str, company: str) -> Optional[Dict[str, Any]]:
    """
    Test the prospect enrichment function

    Args:
        name: Full name of the person
        company: Company name

    Returns:
        Enriched data or None if failed
    """
    print(f"\nTesting prospect enrichment for: {name} at {company}")

    try:
        enriched_data = await apollo_service.enrich_prospect_data(name, company)

        logger.info(f"Enrichment completed for {name}")
        print_json(enriched_data, f"Enriched Data for {name}")

        # Check if enrichment was successful
        basic_info = enriched_data.get("basic_info", {})
        is_enriched = basic_info.get("enriched", False)

        if is_enriched:
            logger.info("Data enrichment successful")
        else:
            logger.warning("Data enrichment failed or returned no data")
            error = basic_info.get("error", "Unknown error")
            print(f"Enrichment error: {error}")

        return enriched_data

    except Exception as e:
        logger.error(f"Error enriching data for {name}: {e}")
        print(f"Enrichment failed: {str(e)}")
        return None

async def run_api_tests() -> None:
    """Run comprehensive Apollo.io API tests"""

    print_header("Apollo.io API Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check API key configuration
    api_key = os.environ.get("APOLLO_API_KEY")
    if not api_key:
        print("\nAPOLLO_API_KEY environment variable not found!")
        print("Please set your Apollo.io API key:")
        print("export APOLLO_API_KEY=your-api-key-here")
        print("\nOr add it to your .env file:")
        print("APOLLO_API_KEY=your-api-key-here")
        return

    print(f"API Key configured: {api_key[:10]}...{api_key[-4:]}")
    print(f"Apollo service initialized: {apollo_service is not None}")

    # Test cases
    test_cases = [
        ("John Smith", "Google"),
        ("Sarah Johnson", "Microsoft"),
        ("Carlos Silva", "Nubank"),  # Brazilian company
        ("Tim Cook", "Apple")  # High-profile CEO
    ]

    results = []

    for name, company in test_cases:
        print_header(f"Testing: {name} @ {company}")

        try:
            # Test basic search
            search_result = await test_person_search(name, company)

            # Test enrichment
            enrichment_result = await test_prospect_enrichment(name, company)

            results.append({
                "name": name,
                "company": company,
                "search_successful": search_result is not None,
                "enrichment_successful": enrichment_result is not None and
                                       enrichment_result.get("basic_info", {}).get("enriched", False),
                "search_result": search_result,
                "enrichment_result": enrichment_result
            })

        except Exception as e:
            logger.error(f"Test case failed for {name} @ {company}: {e}")
            results.append({
                "name": name,
                "company": company,
                "search_successful": False,
                "enrichment_successful": False,
                "error": str(e)
            })

    # Print summary
    print_header("Test Results Summary")

    successful_searches = sum(1 for r in results if r.get("search_successful", False))
    successful_enrichments = sum(1 for r in results if r.get("enrichment_successful", False))
    total_tests = len(results)

    print(f"Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful searches: {successful_searches}/{total_tests}")
    print(f"   Successful enrichments: {successful_enrichments}/{total_tests}")
    print(f"   Success rate: {(successful_searches/total_tests)*100:.1f}%")

    # Print detailed results
    print_json(results, "Detailed Test Results")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def main():
    """Main function to run the Apollo.io tests"""
    try:
        # Load environment variables from .env file if it exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            logger.info("python-dotenv not available, using environment variables directly")

        # Run the async tests
        asyncio.run(run_api_tests())

    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()