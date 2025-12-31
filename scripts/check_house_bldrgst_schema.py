"""
Check house_bldrgst table schema.

Usage:
    python -m scripts.check_house_bldrgst_schema
"""
from infrastructure.db.postgres import SessionLocal
from sqlalchemy import inspect

def main():
    """Check house_bldrgst table schema."""
    db = SessionLocal()
    try:
        inspector = inspect(db.bind)

        # Check if table exists
        if 'house_bldrgst' not in inspector.get_table_names():
            print("ERROR: Table 'house_bldrgst' does not exist!")
            return

        print("SUCCESS: Table 'house_bldrgst' exists\n")
        print("=" * 80)
        print("COLUMNS:")
        print("=" * 80)

        columns = inspector.get_columns('house_bldrgst')
        for col in columns:
            print(f"  {col['name']:30} {str(col['type']):20} nullable={col['nullable']}")

        print("\n" + "=" * 80)
        print("PRIMARY KEYS:")
        print("=" * 80)
        pk = inspector.get_pk_constraint('house_bldrgst')
        print(f"  {pk['constrained_columns']}")

        print("\n" + "=" * 80)
        print("FOREIGN KEYS:")
        print("=" * 80)
        fks = inspector.get_foreign_keys('house_bldrgst')
        for fk in fks:
            print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
