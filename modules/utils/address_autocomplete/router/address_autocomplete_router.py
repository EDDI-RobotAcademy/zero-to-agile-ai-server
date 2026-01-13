from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session  # 실제 프로젝트 경로에 맞게 수정
from modules.utils.address_autocomplete.usecase.address_autocomplete_usecase import AddressAutocompleteUseCase

router = APIRouter()



@router.get("/autocomplete", response_model=List[str])
def autocomplete_address(
    q: str = Query(..., description="검색 prefix. 예: '서', '서울', '서울특'"),
    db: Session = Depends(get_db_session),
):
    """
    입력값: '서' -> '서울' -> '서울특' -> '서울특별'
    매 타이핑마다 프론트에서 호출하도록 설계.
    목록 제한 없이 전부 반환.
    """
    usecase = AddressAutocompleteUseCase(db)
    result = usecase.execute(q)

    return result