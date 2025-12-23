from abc import ABC, abstractmethod
from typing import Optional, List
from modules.finder_request.domain.finder_request import FinderRequest


class FinderRequestRepositoryPort(ABC):
    """
    FinderRequest Repository의 포트 (인터페이스)
    Application Layer가 의존하는 추상화
    """
    
    @abstractmethod
    def create(self, finder_request: FinderRequest) -> FinderRequest:
        """
        새로운 요구서 생성
        
        Args:
            finder_request: 생성할 요구서 도메인 모델
            
        Returns:
            생성된 요구서 (ID 포함)
        """
        pass
    
    @abstractmethod
    def find_by_id(self, finder_request_id: int) -> Optional[FinderRequest]:
        """
        ID로 요구서 조회
        
        Args:
            finder_request_id: 요구서 ID
            
        Returns:
            요구서 도메인 모델 또는 None
        """
        pass
    
    @abstractmethod
    def find_by_user_id(self, abang_user_id: int) -> List[FinderRequest]:
        """
        사용자 ID로 요구서 목록 조회
        
        Args:
            abang_user_id: 임차인 사용자 ID
            
        Returns:
            요구서 도메인 모델 리스트
        """
        pass
    
    @abstractmethod
    def update(self, finder_request: FinderRequest) -> Optional[FinderRequest]:
        """
        요구서 수정
        
        Args:
            finder_request: 수정할 요구서 도메인 모델 (ID 포함)
            
        Returns:
            수정된 요구서 또는 None
        """
        pass
    
    @abstractmethod
    def delete(self, finder_request_id: int) -> bool:
        """
        요구서 삭제 (hard delete - 실제 DB row 삭제)
        
        Args:
            finder_request_id: 요구서 ID
            
        Returns:
            삭제 성공 여부
        """
        pass
