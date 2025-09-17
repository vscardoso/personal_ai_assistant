#!/usr/bin/env python3
"""
Test script for Sales Assistant models.
Tests Campaign, Prospect, and EmailSequence models.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.database import (
    get_db, Campaign, Prospect, EmailSequence,
    create_campaign, create_prospect, create_email_sequence,
    get_user_campaigns, get_campaign_prospects, get_prospect_emails
)

def test_sales_models():
    """Test all sales assistant models."""
    print("Testing Sales Assistant Models")
    print("=" * 50)

    # Get database session
    db = next(get_db())

    try:
        # Test 1: Create Campaign
        print("1. Creating test campaign...")
        campaign = create_campaign(
            db=db,
            user_id=1,  # Assuming we have a user with ID 1
            name="Q4 Software Sales Campaign",
            description="Targeting software companies for Q4 pipeline"
        )
        print(f"Campaign created: {campaign}")

        # Test 2: Create Prospect
        print("\n2. Creating test prospect...")
        research_data = {
            "company_size": "50-100",
            "industry": "SaaS",
            "tech_stack": ["Python", "React", "AWS"],
            "pain_points": ["Manual processes", "Scaling issues"]
        }

        prospect = create_prospect(
            db=db,
            campaign_id=campaign.id,
            name="John Smith",
            email="john.smith@example.com",
            company="TechCorp Inc",
            title="VP of Engineering",
            linkedin_url="https://linkedin.com/in/johnsmith",
            research_data=research_data
        )
        print(f"Prospect created: {prospect}")

        # Test 3: Create Email Sequence
        print("\n3. Creating email sequence...")
        from datetime import datetime, timedelta

        # First email
        email1 = create_email_sequence(
            db=db,
            prospect_id=prospect.id,
            step=1,
            subject="Quick question about TechCorp's scaling challenges",
            body="Hi John,\n\nI noticed TechCorp has been growing rapidly...",
            template_name="cold_outreach_1",
            scheduled_for=datetime.utcnow() + timedelta(minutes=5)
        )

        # Follow-up email
        email2 = create_email_sequence(
            db=db,
            prospect_id=prospect.id,
            step=2,
            subject="Re: Scaling solutions for TechCorp",
            body="Hi John,\n\nFollowing up on my previous email...",
            template_name="follow_up_1",
            scheduled_for=datetime.utcnow() + timedelta(days=3)
        )

        print(f"Email sequence created: {email1}, {email2}")

        # Test 4: Query Functions
        print("\n4. Testing query functions...")

        # Get user campaigns
        campaigns = get_user_campaigns(db, user_id=1)
        print(f"User campaigns: {len(campaigns)} found")

        # Get campaign prospects
        prospects = get_campaign_prospects(db, campaign_id=campaign.id)
        print(f"Campaign prospects: {len(prospects)} found")

        # Get prospect emails
        emails = get_prospect_emails(db, prospect_id=prospect.id)
        print(f"Prospect emails: {len(emails)} found")

        # Test 5: Relationships
        print("\n5. Testing relationships...")
        print(f"Campaign → Prospects: {len(campaign.prospects)}")
        print(f"Prospect → Emails: {len(prospect.email_sequences)}")
        print(f"Campaign total prospects: {campaign.total_prospects}")

        print("\nAll sales models tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_sales_models()
    sys.exit(0 if success else 1)