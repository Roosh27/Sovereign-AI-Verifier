from sqlalchemy import inspect
from models import engine, Base, init_db
import os
import shutil
from datetime import datetime

def migrate_database():
    """Drop old table and recreate with new schema."""
    
    # Backup existing database
    if os.path.exists('sovereign_ai.db'):
        backup_name = f"sovereign_ai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy('sovereign_ai.db', backup_name)
        print(f"✅ Backup created: {backup_name}")
        
        # Remove old database
        os.remove('sovereign_ai.db')
        print("✅ Old database removed")
    
    # Create new database with clean schema
    init_db()
    print("✅ New database created with clean schema")
    print("\n📋 Current Applications table columns:")
    
    # Verify new schema
    inspector = inspect(engine)
    columns = inspector.get_columns('applications')
    for col in columns:
        print(f"   - {col['name']}: {col['type']}")

if __name__ == "__main__":
    migrate_database()