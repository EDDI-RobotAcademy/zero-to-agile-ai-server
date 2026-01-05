"""
도메인 예외 클래스
"""


class HouseAnalysisError(Exception):
    """House Analysis 모듈의 기본 예외 클래스"""
    pass


class InvalidAddressError(HouseAnalysisError):
    """유효하지 않은 주소 예외"""
    pass


class BuildingInfoNotFoundError(HouseAnalysisError):
    """건축물 정보를 찾을 수 없는 경우 예외"""
    pass
