"""
Building Ledger API Client.

This module provides a client for accessing the Building Ledger API (건축물대장 API)
from the Public Data Portal.
"""
import xml.etree.ElementTree as ET
import requests
from typing import Dict, Optional
from infrastructure.config import get_settings


class BuildingLedgerAPIError(Exception):
    """Base exception for Building Ledger API errors."""
    pass


class BuildingLedgerNotFoundError(BuildingLedgerAPIError):
    """Exception raised when building data is not found."""
    pass


class BuildingLedgerRateLimitError(BuildingLedgerAPIError):
    """Exception raised when API rate limit is exceeded."""
    pass


class BuildingLedgerClient:
    """
    Client for Building Ledger API.

    This client handles:
    - HTTP requests to the Building Ledger API
    - XML response parsing
    - Error handling and retries
    """

    def __init__(self):
        """Initialize the Building Ledger API client."""
        settings = get_settings()
        self.api_key = settings.PUBLIC_DATA_API_KEY
        self.endpoint = settings.BUILDING_LEDGER_API_ENDPOINT
        self.timeout = 10  # seconds

    def get_building_info(
        self,
        sigungu_cd: str,
        bjdong_cd: str,
        bun: Optional[str] = None,
        ji: Optional[str] = None
    ) -> Dict:
        """
        Get building information from Building Ledger API.

        Args:
            sigungu_cd: 시군구 코드 (5 digits)
            bjdong_cd: 법정동 코드 (5 digits)
            bun: 번 (building number)
            ji: 지 (sub-number)

        Returns:
            Dictionary containing building information

        Raises:
            ValueError: If required parameters are missing or invalid
            BuildingLedgerAPIError: If API request fails
            BuildingLedgerNotFoundError: If building is not found
            BuildingLedgerRateLimitError: If rate limit is exceeded
        """
        # Validate required parameters
        if not sigungu_cd or not sigungu_cd.strip():
            raise ValueError("sigungu_cd is required and cannot be empty")
        if not bjdong_cd or not bjdong_cd.strip():
            raise ValueError("bjdong_cd is required and cannot be empty")

        # Make API request
        return self._make_request(
            sigungu_cd=sigungu_cd,
            bjdong_cd=bjdong_cd,
            bun=bun,
            ji=ji
        )

    def _make_request(
        self,
        sigungu_cd: str,
        bjdong_cd: str,
        bun: Optional[str] = None,
        ji: Optional[str] = None
    ) -> Dict:
        """
        Make HTTP request to Building Ledger API.

        Args:
            sigungu_cd: 시군구 코드
            bjdong_cd: 법정동 코드
            bun: 번
            ji: 지

        Returns:
            Parsed building information dictionary

        Raises:
            BuildingLedgerAPIError: If request fails
        """
        # Prepare request parameters
        params = {
            'serviceKey': self.api_key,
            'sigunguCd': sigungu_cd,
            'bjdongCd': bjdong_cd,
            'numOfRows': 10,
            'pageNo': 1
        }

        if bun:
            params['bun'] = bun
        if ji:
            params['ji'] = ji

        try:
            # Make HTTP GET request
            response = requests.get(
                self.endpoint,
                params=params,
                timeout=self.timeout
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Parse XML response
            return self._parse_xml(response.text)

        except requests.Timeout as e:
            raise BuildingLedgerAPIError(f"Request timeout: {str(e)}")
        except requests.RequestException as e:
            raise BuildingLedgerAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            raise BuildingLedgerAPIError(f"Unexpected error: {str(e)}")

    def _parse_xml(self, xml_text: str) -> Dict:
        """
        Parse XML response from Building Ledger API.

        Args:
            xml_text: XML response text

        Returns:
            Dictionary containing parsed building information

        Raises:
            BuildingLedgerNotFoundError: If no data found (resultCode 03)
            BuildingLedgerRateLimitError: If rate limit exceeded (resultCode 22)
            BuildingLedgerAPIError: For other API errors
        """
        try:
            root = ET.fromstring(xml_text)

            # Check response status
            self._check_response_status(root)

            # Extract building data
            return self._extract_building_data(root)

        except ET.ParseError as e:
            raise BuildingLedgerAPIError(f"XML parsing error: {str(e)}")
        except (BuildingLedgerNotFoundError, BuildingLedgerRateLimitError):
            raise
        except Exception as e:
            raise BuildingLedgerAPIError(f"Error parsing response: {str(e)}")

    def _check_response_status(self, root: ET.Element) -> None:
        """
        Check API response status for errors.

        Args:
            root: XML root element

        Raises:
            BuildingLedgerNotFoundError: If data not found
            BuildingLedgerRateLimitError: If rate limit exceeded
            BuildingLedgerAPIError: For other errors
        """
        header = root.find('header')
        if header is None:
            return

        result_code = header.findtext('resultCode', '')
        result_msg = header.findtext('resultMsg', '')

        if result_code == '00':
            return  # Success

        # Map error codes to exceptions
        if result_code == '03':
            raise BuildingLedgerNotFoundError(
                f"No data found (Code: {result_code}, Message: {result_msg})"
            )
        elif result_code == '22':
            raise BuildingLedgerRateLimitError(
                f"Rate limit exceeded (Code: {result_code}, Message: {result_msg})"
            )
        else:
            raise BuildingLedgerAPIError(
                f"API error (Code: {result_code}, Message: {result_msg})"
            )

    def _extract_building_data(self, root: ET.Element) -> Dict:
        """
        Extract building information from XML body.

        Args:
            root: XML root element

        Returns:
            Dictionary containing building information

        Raises:
            BuildingLedgerAPIError: If body structure is invalid
            BuildingLedgerNotFoundError: If no building data found
        """
        body = root.find('body')
        if body is None:
            raise BuildingLedgerAPIError("Response body not found")

        items = body.find('items')
        if items is None:
            raise BuildingLedgerAPIError("Items not found in response")

        item = items.find('item')
        if item is None:
            raise BuildingLedgerNotFoundError("No building data found")

        # Extract all fields from item
        building_info = {child.tag: child.text for child in item}

        return building_info

    def get_building_info_by_address(
        self,
        address: str,
        db
    ) -> Dict:
        """
        Fetch building ledger info using full address string.

        This is a convenience method that parses the address and calls get_building_info().

        Args:
            address: Full address (e.g., "서울시 강남구 역삼동 777-88")
            db: Database session for bjdong code lookup

        Returns:
            Building ledger data dictionary

        Raises:
            AddressParsingError: If address format is invalid
            BjdongCodeNotFoundError: If legal dong code is not found in database
            BuildingLedgerAPIError: If API request fails
        """
        from modules.risk_analysis.application.service.address_parser_service import AddressParserService

        parser = AddressParserService(db)
        codes = parser.parse_address_and_get_codes(address)

        return self.get_building_info(
            sigungu_cd=codes["sigungu_cd"],
            bjdong_cd=codes["bjdong_cd"],
            bun=codes["bun"],
            ji=codes["ji"]
        )
