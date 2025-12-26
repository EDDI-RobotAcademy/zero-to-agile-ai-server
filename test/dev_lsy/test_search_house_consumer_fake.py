# # test/dev_lsy/test_search_house_consumer_fake.py
# # pytest test/dev_lsy/test_search_house_consumer_fake.py
#
# from sqlalchemy.orm import Session
#
# from infrastructure.db.postgres import get_db_session
# from modules.mq.adapter.output.repository.search_house_repository import (
#     SearchHouseRepository,
# )
# from modules.mq.application.usecase.process_search_house_usecase import (
#     ProcessSearchHouseUseCase,
# )
#
# # ---------- Fake AI Result ----------
# FAKE_AI_RESULT = {
#     "recommended_houses": [
#         {
#             "house_platform_id": 101,
#             "score": 92,
#             "reason": "직주근접 + 리스크 낮음",
#         }
#     ],
#     "confidence": 0.91,
# }
#
#
# class FakeSearchHouseAgent:
#     def run(self, search_house_id: int) -> dict:
#         return FAKE_AI_RESULT
#
#
# def test_process_search_house_success():
#     """
#     목적:
#     - QUEUED 상태 job을
#       PROCESSING → COMPLETED 까지 정상 전이
#     - result_json 이 저장되는지 검증
#     """
#
#     # 1️⃣ DB 세션 준비
#     db: Session = next(get_db_session())
#
#     repo = SearchHouseRepository(db)
#
#     # ⚠️ 테스트용 job_id (이미 QUEUED 상태여야 함)
#     search_house_id = 30  # 네 DB에 존재하는 값으로 맞춰
#
#     # 2️⃣ Fake Agent 주입
#     fake_agent = FakeSearchHouseAgent()
#
#     # 3️⃣ UseCase 생성
#     usecase = ProcessSearchHouseUseCase(
#         db=db,
#         ai_agent=fake_agent,
#     )
#
#     # 4️⃣ 실행
#     usecase.execute(search_house_id)
#
#     # 5️⃣ 결과 검증
#     entity = repo.get_by_id(search_house_id)
#
#     assert entity.status == "COMPLETED"
#     assert entity.result_json is not None
#     assert entity.result_json["confidence"] == 0.91