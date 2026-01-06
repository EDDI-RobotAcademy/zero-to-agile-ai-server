from sqlalchemy.orm import Session
from typing import Optional, List
from modules.finder_request.application.port.finder_request_repository_port import FinderRequestRepositoryPort
from modules.finder_request.domain.finder_request import FinderRequest
from modules.finder_request.adapter.output.finder_request_model import FinderRequestModel


class FinderRequestRepository(FinderRequestRepositoryPort):
    """
    FinderRequest Repository 구현체
    PostgreSQL을 사용한 영속성 관리
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    # def __init__(self, db_session_factory):
    #     self.db_session_factory = db_session_factory
    
    def create(self, finder_request: FinderRequest) -> FinderRequest:
        """
        새로운 요구서 생성
        
        Args:
            finder_request: 생성할 요구서 도메인 모델
            
        Returns:
            생성된 요구서 (ID 포함)
        """
        #db: Session = self.db_session_factory()
        try:
            # 도메인 모델 → ORM 모델 변환
            model = FinderRequestModel(
                abang_user_id=finder_request.abang_user_id,
                preferred_region=finder_request.preferred_region,
                price_type=finder_request.price_type,
                max_deposit=finder_request.max_deposit,
                max_rent=finder_request.max_rent,
                status=finder_request.status,
                house_type=finder_request.house_type,
                additional_condition=finder_request.additional_condition,
                university_name=finder_request.university_name
            )
            
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            
            # ORM 모델 → 도메인 모델 변환
            return self._to_domain(model)
        finally:
            self.db.close()
    
    def find_by_id(self, finder_request_id: int) -> Optional[FinderRequest]:
        """
        ID로 요구서 조회
        
        Args:
            finder_request_id: 요구서 ID
            
        Returns:
            요구서 도메인 모델 또는 None
        """
        #db: Session = self.db_session_factory()
        #try:
        model = self.db.query(FinderRequestModel).filter(
            FinderRequestModel.finder_request_id == finder_request_id
        ).first()

        if not model:
            return None

        return self._to_domain(model)
        # finally:
        #     self.db.close()
    
    def _to_domain(self, model: FinderRequestModel) -> FinderRequest:
        """ORM 모델을 도메인 모델로 변환"""
        return FinderRequest(
            abang_user_id=model.abang_user_id,
            status=model.status,
            finder_request_id=model.finder_request_id,
            preferred_region=model.preferred_region,
            price_type=model.price_type,
            max_deposit=model.max_deposit,
            max_rent=model.max_rent,
            house_type=model.house_type,
            additional_condition=model.additional_condition,
            university_name=model.university_name,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def find_by_user_id(self, abang_user_id: int) -> List[FinderRequest]:
        """
        사용자 ID로 요구서 목록 조회 (모든 status 포함)
        
        Args:
            abang_user_id: 임차인 사용자 ID
            
        Returns:
            요구서 도메인 모델 리스트
        """
        #db: Session = self.db_session_factory()
        try:
            models = self.db.query(FinderRequestModel).filter(
                FinderRequestModel.abang_user_id == abang_user_id
            ).order_by(FinderRequestModel.created_at.desc()).all()
            
            return [self._to_domain(model) for model in models]
        finally:
            self.db.close()
    
    def update(self, finder_request: FinderRequest) -> Optional[FinderRequest]:
        """
        요구서 수정
        
        Args:
            finder_request: 수정할 요구서 도메인 모델 (ID 포함)
            
        Returns:
            수정된 요구서 또는 None (존재하지 않는 경우)
        """
        #db: Session = self.db_session_factory()
        try:
            model = self.db.query(FinderRequestModel).filter(
                FinderRequestModel.finder_request_id == finder_request.finder_request_id
            ).first()

            if not model:
                return None

            # 업데이트 가능한 필드만 변경
            if finder_request.preferred_region is not None:
                model.preferred_region = finder_request.preferred_region
            if finder_request.price_type is not None:
                model.price_type = finder_request.price_type
            if finder_request.max_deposit is not None:
                model.max_deposit = finder_request.max_deposit
            if finder_request.max_rent is not None:
                model.max_rent = finder_request.max_rent
            if finder_request.house_type is not None:
                model.house_type = finder_request.house_type
            if finder_request.additional_condition is not None:
                model.additional_condition = finder_request.additional_condition
            if finder_request.university_name is not None:
                model.university_name = finder_request.university_name
            if finder_request.status is not None:
                model.status = finder_request.status

            self.db.commit()
            self.db.refresh(model)

            return self._to_domain(model)
        finally:
            self.db.close()
    
    def delete(self, finder_request_id: int) -> bool:
        """
        요구서 삭제 (hard delete - 실제 row 삭제)
        
        Args:
            finder_request_id: 요구서 ID
            
        Returns:
            삭제 성공 여부
        """
        #db: Session = self.db_session_factory()
        try:
            print(f"🔍 [HARD DELETE] finder_request_id={finder_request_id} 조회 시도")
            
            model = self.db.query(FinderRequestModel).filter(
                FinderRequestModel.finder_request_id == finder_request_id
            ).first()
            
            if not model:
                print(f"❌ [HARD DELETE] finder_request_id={finder_request_id} 찾을 수 없음")
                return False
            
            print(f"✅ [HARD DELETE] 조회 성공: finder_request_id={model.finder_request_id}")
            print(f"   abang_user_id: {model.abang_user_id}")
            print(f"   status: {model.status}")
            
            # ✅ HARD DELETE 수행 - 실제 row 삭제
            self.db.delete(model)
            print(f"🗑️  [HARD DELETE] db.delete() 호출 완료")
            
            # ✅ 명시적 flush
            self.db.flush()
            print(f"✅ [HARD DELETE] flush 완료")
            
            # ✅ 커밋
            self.db.commit()
            print(f"✅ [HARD DELETE] commit 완료")
            
            # ✅ 삭제 검증 - 다시 조회했을 때 없어야 함
            verify = self.db.query(FinderRequestModel).filter(
                FinderRequestModel.finder_request_id == finder_request_id
            ).first()
            
            if verify is not None:
                print(f"❌ [HARD DELETE] 검증 실패: row가 여전히 존재함")
                self.db.rollback()
                return False
            
            print(f"✅ [HARD DELETE] 삭제 성공: finder_request_id={finder_request_id} row가 완전히 제거됨")
            return True
            
        except Exception as e:
            # ✅ 예외 발생 시 롤백 및 실패 반환
            print(f"❌ [HARD DELETE] 예외 발생: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            return False
        finally:
            self.db.close()
