# """
# 이 테스트는 매물 추천 로직(추천 AI 에이전트) 팀원을 위한
# '호출 스타트 포인트 계약 테스트'이다.
#
# 이 파일을 기준으로:
# - 매물 추천 로직은 어디서 호출되는지
# - 어떤 입력을 받는지
# - 어떤 출력 형식을 반환해야 하는지
# 를 정의한다.
#
# <전달사항>
# 	•	매물 추천 로직은 ProcessSearchHouseUseCase.execute() 안에서 호출됩니다
# 	•	입력은 finder_request 도메인 객체입니다
# 	•	출력은 JSON(dict) 하나면 됩니다
# 	•	DB 저장, 상태 전이는 매물 추천 로직이 하지 않습니다
# 	•	예외만 던지면 FAILED 처리는 자동입니다
# """
#
# from sqlalchemy.orm import Session
#
# from infrastructure.db.postgres import get_db_session
# from modules.mq.adapter.output.repository.search_house_repository import (
#     SearchHouseRepository,
# )
# from modules.finder_request.adapter.output.repository.finder_request_repository import (
#     FinderRequestRepository,
# )
# from modules.mq.application.usecase.process_search_house_usecase import (
#     ProcessSearchHouseUseCase,
# )
#
# # -------------------------------
# # 매물 추천 로직이 반드시 구현해야 하는 인터페이스
# # -------------------------------
#
# class BLogicAgentInterface:
#     """
#     매물 추천 로직(AI 에이전트) 팀원이 구현해야 할 최소 인터페이스
#     """
#
#     def run(self, finder_request) -> dict:
#         """
#         Args:
#             finder_request:
#                 - finder_request 테이블에서 조회된 도메인 객체
#                 - 매물 조건, 예산, 선호 지역 등을 포함
#
#         Returns:
#             dict: 반드시 JSON serializable 해야 함
#         """
#         raise NotImplementedError
#
#
# # -------------------------------
# # 테스트용 Fake 매물 추천 로직
# # -------------------------------
#
# class FakeBLogicAgent(BLogicAgentInterface):
#     """
#     실제 AI 로직 대신, 계약 검증용 Fake 구현
#     """
#
#     def run(self, finder_request) -> dict:
#         return {
#             "recommended_houses": [
#                 {
#                     "house_platform_id": 101,
#                     "score": 92,
#                     "reason": "직주근접 + 리스크 낮음",
#                 }
#             ],
#             "confidence": 0.91,
#             "source_finder_request_id": finder_request.finder_request_id,
#         }
#
#
# # -------------------------------
# # 추천 테스트
# # -------------------------------
#
# def test_b_logic_entrypoint_contract():
#     """
#     목적:
#     - 매물 추천 로직은 'ProcessSearchHouseUseCase'에서 호출된다
#     - 매물 추천 로직 입력은 finder_request 도메인 객체다
#     - 매물 추천 로직 출력은 dict(JSON)이다
#     - 결과는 search_house.result_json에 저장된다
#     """
#
#     # 1️⃣ DB 세션 (Consumer 진입점)
#     db: Session = next(get_db_session())
#
#     search_house_repo = SearchHouseRepository(db)
#     finder_request_repo = FinderRequestRepository(db)
#
#     # 2️⃣ 테스트용 job 생성 (항상 새로)
#     finder_request_id = 12  # 실제 존재하는 ID
#     search_house_id = search_house_repo.create_pending(
#         finder_request_id=finder_request_id
#     )
#     search_house_repo.mark_queued(search_house_id)
#
#     # 3️⃣ Fake 매물 추천 로직 주입
#     fake_b_logic = FakeBLogicAgent()
#
#     # 4️⃣ Consumer UseCase 실행 (🔥 매물 추천 로직 호출 지점)
#     usecase = ProcessSearchHouseUseCase(
#         db=db,
#         ai_agent=fake_b_logic,
#     )
#     usecase.execute(search_house_id)
#
#     # 5️⃣ 결과 검증
#     entity = search_house_repo.get_by_id(search_house_id)
#
#     assert entity.status == "COMPLETED"
#     assert entity.result_json is not None
#     assert entity.result_json["confidence"] == 0.91
#     assert (
#         entity.result_json["source_finder_request_id"]
#         == finder_request_id
#     )