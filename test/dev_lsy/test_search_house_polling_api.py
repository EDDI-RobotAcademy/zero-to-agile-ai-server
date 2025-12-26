# """
# A 로직에서 큐 상태 polling을 테스트하기 위한 코드
#
# 목적:
# - search_house_id로 상태 조회 가능
# - PROCESSING / COMPLETED 상태에 따라 응답이 달라짐
# """
#
# from fastapi.testclient import TestClient
#
# from app.main import app
# from infrastructure.db.postgres import get_db_session
# from modules.mq.adapter.output.repository.search_house_repository import (
#     SearchHouseRepository,
# )
#
# client = TestClient(app)
#
#
# def test_search_house_polling_flow():
#     """
#     NOTE: This test assumes that a search_house row with the given search_house_id
#     and its corresponding finder_request_id already exist in the database.
#     You must manually ensure that the search_house_id below exists for this test to pass.
#     """
#     # 1️⃣ DB 세션
#     db = next(get_db_session())
#     repo = SearchHouseRepository(db)
#     try:
#         # 2️⃣ 이미 존재하는 search_house_id를 사용 (사전에 DB에 row가 있어야 함)
#         # ⚠️ 이 값은 실제 DB에 존재해야 함!
#         search_house_id = 12
#         # 3️⃣ PENDING → QUEUED 상태로 (이미 있다면 중복 호출 무방)
#         repo.mark_queued(search_house_id)
#
#         # 4️⃣ (가짜) 처리 중 상태 확인
#         response = client.get(f"/search_house/{search_house_id}")
#         assert response.status_code == 200
#         assert response.json()["status"] in ("QUEUED", "PROCESSING")
#
#         # 5️⃣ 결과를 가짜로 완료 처리
#         repo.mark_processing(search_house_id)
#         repo.save_result(
#             search_house_id,
#             result={"dummy": "result"}
#         )
#         repo.mark_completed(search_house_id)
#
#         # 6️⃣ 완료 후 polling
#         response = client.get(f"/search_house/{search_house_id}")
#         body = response.json()
#
#         assert body["status"] == "COMPLETED"
#         assert body["result"] == {"dummy": "result"}
#     finally:
#         db.close()