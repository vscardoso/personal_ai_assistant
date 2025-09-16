#!/usr/bin/env python3
"""
Personal AI Assistant - Development Runner
Simple script to run the application in development mode.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if all necessary files exist."""
    required_files = [
        ".env",
        "app/main.py",
        "requirements.txt"
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False

    print("✅ All required files found")
    return True

def install_dependencies():
    """Install dependencies if needed."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def run_server():
    """Run the FastAPI server."""
    print("🚀 Starting Personal AI Assistant...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop\n")

    try:
        subprocess.run([
            "uvicorn", "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start server")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True

def main():
    """Main function."""
    print("🤖 Personal AI Assistant - Development Runner")
    print("=" * 50)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Run server
    run_server()

if __name__ == "__main__":
    main()