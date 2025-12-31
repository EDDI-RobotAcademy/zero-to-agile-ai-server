"""
Manual verification script for address parsing and bjdong code lookup.

Usage:
    python -m scripts.verify_address_lookup
"""
import sys
from infrastructure.db.postgres import SessionLocal
from modules.risk_analysis.application.service.address_parser_service import (
    AddressParserService,
    AddressParsingError,
    BjdongCodeNotFoundError
)


def main():
    """Main verification function."""
    print("=" * 60)
    print("Address Parsing & Bjdong Code Lookup Verification")
    print("=" * 60)

    # Test addresses
    test_addresses = [
        "서울시 강남구 역삼동 777-88",
        "서울특별시 종로구 효자동 123",
        "부산시 해운대구 우동 456-78",
    ]

    db = SessionLocal()
    try:
        parser = AddressParserService(db)

        for address in test_addresses:
            print(f"\n{'='*60}")
            print(f"Input Address: {address}")
            print(f"{'='*60}")

            try:
                result = parser.parse_address_and_get_codes(address)
                print(f"✅ SUCCESS")
                print(f"  Sigungu Code: {result['sigungu_cd']}")
                print(f"  Bjdong Code:  {result['bjdong_cd']}")
                print(f"  Bun:          {result['bun']}")
                print(f"  Ji:           {result['ji']}")
            except AddressParsingError as e:
                print(f"❌ PARSING ERROR: {e}")
            except BjdongCodeNotFoundError as e:
                print(f"❌ CODE NOT FOUND: {e}")
            except Exception as e:
                print(f"❌ UNEXPECTED ERROR: {e}")

    finally:
        db.close()

    print(f"\n{'='*60}")
    print("Verification Complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
