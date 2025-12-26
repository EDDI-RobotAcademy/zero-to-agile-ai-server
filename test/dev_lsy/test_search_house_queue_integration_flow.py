# """
# Queue End-to-End Integration Test
#
# 목적:
# - finder_request_id → search_house 생성
# - consumer 처리
# - polling API로 최종 결과 확인
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
# def test_search_house_queue_integration_flow():
#     # 1️⃣ 사전 조건: 실제 존재하는 finder_request_id
#     finder_request_id = 12  # 반드시 DB에 존재해야 함
#
#     db = next(get_db_session())
#     repo = SearchHouseRepository(db)
#
#     try:
#         # =========================
#         # [A] Producer 단계
#         # =========================
#         search_house_id = repo.create_pending(finder_request_id)
#         repo.mark_queued(search_house_id)
#
#         # =========================
#         # [B] Consumer 단계 (가짜 B 로직)
#         # =========================
#         repo.mark_processing(search_house_id)
#
#         fake_result = {
#             "recommended_house_ids": [101, 102, 103],
#             "reason": "조건 기반 추천",
#             "score": 0.92,
#         }
#
#         repo.save_result(search_house_id, fake_result)
#         repo.mark_completed(search_house_id)
#
#         # =========================
#         # [A] Polling API 단계
#         # =========================
#         response = client.get(f"/api/search_house/{search_house_id}")
#         assert response.status_code == 200
#
#         body = response.json()
#
#         assert body["status"] == "COMPLETED"
#         assert body["result"] == fake_result
#
#     finally:
#         db.close()