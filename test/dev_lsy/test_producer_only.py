# """
# Producer 단독 테스트
# - FastAPI 서버 실행 중이어야 함
# - Consumer 없음
# - RabbitMQ는 살아 있어야 함
# """
# # pytest test/dev_lsy/test_producer_only.py
#
# import requests
#
# BASE_URL = "http://localhost:33333/api"
#
# def test_enqueue_search_house():
#     payload = {
#         "finder_request_id": 12  # 실제 존재하는 ID
#     }
#
#     response = requests.post(
#         f"{BASE_URL}/search_house",
#         json=payload
#     )
#
#     print("status_code:", response.status_code)
#     print("response:", response.json())
#
#     assert response.status_code == 200
#     assert "search_house_id" in response.json()