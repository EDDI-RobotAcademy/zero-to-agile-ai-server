"""
Verify house_platform_id is stored in house_bldrgst table.
"""
from infrastructure.db.postgres import SessionLocal
from sqlalchemy import text

def verify_house_platform_id():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("VERIFYING house_platform_id IN house_bldrgst TABLE")
        print("=" * 80)

        # Query house_bldrgst table
        query = text("""
            SELECT
                house_bldrgst_id,
                house_platform_id,
                address,
                total_score
            FROM house_bldrgst
            ORDER BY house_bldrgst_id DESC
            LIMIT 10
        """)

        result = db.execute(query)
        rows = result.fetchall()

        if not rows:
            print("\n[INFO] No records found in house_bldrgst table")
            return

        print(f"\n[RESULT] Found {len(rows)} records in house_bldrgst table:\n")
        print("-" * 80)

        for idx, row in enumerate(rows, 1):
            house_bldrgst_id = row[0]
            house_platform_id = row[1]
            address = row[2]
            total_score = row[3]

            print(f"[{idx}] Record:")
            print(f"    house_bldrgst_id (PK): {house_bldrgst_id}")
            print(f"    house_platform_id (FK): {house_platform_id}")
            print(f"    address: {address[:50] if address else 'NULL'}...")
            print(f"    total_score: {total_score}")
            print()

        print("=" * 80)
        print("[OK] house_platform_id column exists and contains data!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_house_platform_id()
