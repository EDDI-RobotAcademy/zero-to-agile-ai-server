import pytest
from abc import ABC, abstractmethod
from modules.house_analysis.application.port.address_codec_port import AddressCodecPort
from modules.house_analysis.application.port.building_ledger_port import BuildingLedgerPort
from modules.house_analysis.application.port.transaction_price_port import TransactionPricePort
from modules.house_analysis.application.port.risk_history_port import RiskHistoryPort
from modules.house_analysis.application.port.price_history_port import PriceHistoryPort
from modules.house_analysis.domain.model import RiskScore, PriceScore


def test_address_codec_port_interface():
    """
    AddressCodecPort 인터페이스 정의 테스트
    - 메서드: convert_to_legal_code(address: str) -> dict
    """
    # Then: AddressCodecPort가 ABC를 상속하는지 확인
    assert issubclass(AddressCodecPort, ABC)

    # Then: convert_to_legal_code 메서드가 abstract method인지 확인
    assert hasattr(AddressCodecPort, 'convert_to_legal_code')
    assert getattr(AddressCodecPort.convert_to_legal_code, '__isabstractmethod__', False)

    # Then: 구현 없이 인스턴스화하면 에러 발생
    with pytest.raises(TypeError):
        AddressCodecPort()


def test_building_ledger_port_interface():
    """
    BuildingLedgerPort 인터페이스 정의 테스트
    - 메서드: fetch_building_info(legal_code: str) -> dict
    """
    # Then: BuildingLedgerPort가 ABC를 상속하는지 확인
    assert issubclass(BuildingLedgerPort, ABC)

    # Then: fetch_building_info 메서드가 abstract method인지 확인
    assert hasattr(BuildingLedgerPort, 'fetch_building_info')
    assert getattr(BuildingLedgerPort.fetch_building_info, '__isabstractmethod__', False)

    # Then: 구현 없이 인스턴스화하면 에러 발생
    with pytest.raises(TypeError):
        BuildingLedgerPort()


def test_transaction_price_port_interface():
    """
    TransactionPricePort 인터페이스 정의 테스트
    - 메서드: fetch_transaction_prices(legal_code: str, deal_type: str) -> list
    """
    # Then: TransactionPricePort가 ABC를 상속하는지 확인
    assert issubclass(TransactionPricePort, ABC)

    # Then: fetch_transaction_prices 메서드가 abstract method인지 확인
    assert hasattr(TransactionPricePort, 'fetch_transaction_prices')
    assert getattr(TransactionPricePort.fetch_transaction_prices, '__isabstractmethod__', False)

    # Then: 구현 없이 인스턴스화하면 에러 발생
    with pytest.raises(TypeError):
        TransactionPricePort()


def test_risk_history_port_interface():
    """
    RiskHistoryPort 인터페이스 정의 테스트
    - 메서드: save(risk_score: RiskScore) -> None
    """
    # Then: RiskHistoryPort가 ABC를 상속하는지 확인
    assert issubclass(RiskHistoryPort, ABC)

    # Then: save 메서드가 abstract method인지 확인
    assert hasattr(RiskHistoryPort, 'save')
    assert getattr(RiskHistoryPort.save, '__isabstractmethod__', False)

    # Then: 구현 없이 인스턴스화하면 에러 발생
    with pytest.raises(TypeError):
        RiskHistoryPort()


def test_price_history_port_interface():
    """
    PriceHistoryPort 인터페이스 정의 테스트
    - 메서드: save(price_score: PriceScore) -> None
    """
    # Then: PriceHistoryPort가 ABC를 상속하는지 확인
    assert issubclass(PriceHistoryPort, ABC)

    # Then: save 메서드가 abstract method인지 확인
    assert hasattr(PriceHistoryPort, 'save')
    assert getattr(PriceHistoryPort.save, '__isabstractmethod__', False)

    # Then: 구현 없이 인스턴스화하면 에러 발생
    with pytest.raises(TypeError):
        PriceHistoryPort()
