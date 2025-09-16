#!/usr/bin/env python3
"""
Database initialization script for Personal AI Assistant.
Creates all tables and can be run in both development and production.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.database import engine, Base, get_db
from models.database import User, Conversation, Relationship

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def check_database_connection():
    """Test database connection."""
    try:
        logger.info("Testing database connection...")
        db = next(get_db())

        # Try a simple query
        user_count = db.query(User).count()
        logger.info(f"✅ Database connection successful! Users in database: {user_count}")

        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def show_database_info():
    """Show database configuration information."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./personal_assistant.db")
    db_type = database_url.split("://")[0]

    logger.info("📊 Database Configuration:")
    logger.info(f"  Database Type: {db_type}")

    if db_type == "sqlite":
        db_path = database_url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            db_path = Path(db_path[2:]).absolute()
        logger.info(f"  Database File: {db_path}")
        logger.info(f"  File Exists: {Path(db_path).exists()}")
    else:
        # Don't log the full URL as it may contain credentials
        logger.info(f"  Database URL: {db_type}://[credentials hidden]")

def main():
    """Main function."""
    logger.info("🤖 Personal AI Assistant - Database Initialization")
    logger.info("=" * 60)

    # Show database info
    show_database_info()

    # Create tables
    if not create_tables():
        sys.exit(1)

    # Test connection
    if not check_database_connection():
        sys.exit(1)

    logger.info("🎉 Database initialization completed successfully!")
    logger.info("The application is ready to run.")

if __name__ == "__main__":
    main()