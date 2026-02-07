#!/usr/bin/env python3
"""
Script untuk create database tables untuk KBCard dan semua models.
Jalankan sebelum seeding: python scripts/create_tables.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import Base, engine
from app.models import Decision, DecisionRevision, ThreatLiteAssessment, KBCard


def create_tables():
    """Create all database tables."""
    print("\n" + "="*80)
    print("🗄️  DATABASE TABLE CREATION")
    print("="*80 + "\n")
    
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables
        from sqlalchemy import inspect, text
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("✅ Tables created successfully:\n")
        for table in tables:
            print(f"  ✓ {table}")
        
        print("\n" + "="*80 + "\n")
        return 0
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return 1


if __name__ == "__main__":
    exit_code = create_tables()
    exit(exit_code)
