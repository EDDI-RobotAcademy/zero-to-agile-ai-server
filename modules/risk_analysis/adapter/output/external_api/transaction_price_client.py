"""
Transaction Price API Client.

This module provides a client for fetching real estate transaction price data
from the Public Data Portal (공공데이터포털) API.
"""
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import requests
from infrastructure.config import get_settings


class TransactionPriceAPIError(Exception):
    """Base exception for Transaction Price API errors."""
    pass


class TransactionPriceNotFoundError(TransactionPriceAPIError):
    """Exception raised when transaction data is not found."""
    pass


class TransactionPriceRateLimitError(TransactionPriceAPIError):
    """Exception raised when API rate limit is exceeded."""
    pass


class TransactionPriceClient:
    """
    Client for the Real Transaction Price API (실거래가 API).

    Fetches apartment transaction price data from the Public Data Portal.
    """

    def __init__(self):
        """Initialize the Transaction Price client with settings."""
        settings = get_settings()
        self.api_key = settings.PUBLIC_DATA_API_KEY
        self.endpoint = settings.TRANSACTION_PRICE_API_ENDPOINT
        self.timeout = 10

    def get_transactions(
        self,
        lawd_cd: str,
        deal_ymd: str
    ) -> List[Dict]:
        """
        Fetch transaction price data for a given region and period.

        Args:
            lawd_cd: Regional code (법정동코드 5자리, e.g., "11440" for Mapo-gu)
            deal_ymd: Transaction year-month (YYYYMM format, e.g., "202411")

        Returns:
            List of transaction records as dictionaries

        Raises:
            ValueError: If required parameters are empty
            TransactionPriceAPIError: If API request fails
            TransactionPriceNotFoundError: If no data is found
            TransactionPriceRateLimitError: If rate limit is exceeded
        """
        if not lawd_cd or not lawd_cd.strip():
            raise ValueError("lawd_cd is required and cannot be empty")
        if not deal_ymd or not deal_ymd.strip():
            raise ValueError("deal_ymd is required and cannot be empty")

        return self._make_request(lawd_cd=lawd_cd, deal_ymd=deal_ymd)

    def _make_request(self, lawd_cd: str, deal_ymd: str) -> List[Dict]:
        """
        Make HTTP request to Transaction Price API.

        Args:
            lawd_cd: Regional code
            deal_ymd: Transaction year-month

        Returns:
            List of transaction records

        Raises:
            TransactionPriceAPIError: If request fails
        """
        params = {
            'serviceKey': self.api_key,
            'LAWD_CD': lawd_cd,
            'DEAL_YMD': deal_ymd,
            'numOfRows': 100,
            'pageNo': 1
        }

        try:
            response = requests.get(self.endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            return self._parse_xml(response.text)
        except requests.Timeout as e:
            raise TransactionPriceAPIError(f"Request timeout: {str(e)}")
        except requests.RequestException as e:
            raise TransactionPriceAPIError(f"Request failed: {str(e)}")

    def _parse_xml(self, xml_text: str) -> List[Dict]:
        """
        Parse XML response from Transaction Price API.

        Args:
            xml_text: XML response text

        Returns:
            List of transaction records

        Raises:
            TransactionPriceAPIError: If XML parsing fails
            TransactionPriceNotFoundError: If no data found
            TransactionPriceRateLimitError: If rate limit exceeded
        """
        try:
            root = ET.fromstring(xml_text)
            self._check_response_status(root)
            return self._extract_transaction_data(root)
        except ET.ParseError as e:
            raise TransactionPriceAPIError(f"XML parsing error: {str(e)}")

    def _check_response_status(self, root: ET.Element) -> None:
        """
        Check API response status and raise appropriate errors.

        Args:
            root: Root element of XML response

        Raises:
            TransactionPriceNotFoundError: If no data found (code 03)
            TransactionPriceRateLimitError: If rate limit exceeded (code 22)
            TransactionPriceAPIError: For other error codes
        """
        header = root.find('header')
        if header is None:
            return

        result_code = header.findtext('resultCode', '')
        result_msg = header.findtext('resultMsg', '')

        if result_code == '00':
            return
        if result_code == '03':
            raise TransactionPriceNotFoundError(
                f"No data found (Code: {result_code}, Message: {result_msg})"
            )
        elif result_code == '22':
            raise TransactionPriceRateLimitError(
                f"Rate limit exceeded (Code: {result_code}, Message: {result_msg})"
            )
        else:
            raise TransactionPriceAPIError(
                f"API error (Code: {result_code}, Message: {result_msg})"
            )

    def _extract_transaction_data(self, root: ET.Element) -> List[Dict]:
        """
        Extract transaction data from XML response.

        Args:
            root: Root element of XML response

        Returns:
            List of transaction records as dictionaries

        Raises:
            TransactionPriceAPIError: If body or items not found
            TransactionPriceNotFoundError: If no transaction items found
        """
        body = root.find('body')
        if body is None:
            raise TransactionPriceAPIError("Response body not found")

        items = body.find('items')
        if items is None:
            raise TransactionPriceAPIError("Items not found in response")

        item_list = items.findall('item')
        if not item_list:
            raise TransactionPriceNotFoundError("No transaction data found")

        transactions = []
        for item in item_list:
            transaction_info = {child.tag: child.text for child in item}
            transactions.append(transaction_info)

        return transactions
