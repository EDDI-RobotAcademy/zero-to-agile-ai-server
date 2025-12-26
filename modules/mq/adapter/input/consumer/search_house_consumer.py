import json
import pika

from infrastructure.external.embedding_agent import OpenAIEmbeddingAgent
from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository
from modules.finder_request.infrastructure.repository.finder_request_embedding_repository import \
    FinderRequestEmbeddingRepository
from modules.mq.application.usecase.process_search_house_usecase import ProcessSearchHouseUseCase
import os
from dotenv import load_dotenv
from infrastructure.db.postgres import get_db_session  # Import DB session factory used by FastAPI router
from modules.student_house.application.usecase.recommend_student_house_for_finder_request import (
    RecommendStudentHouseUseCase,
)
from modules.student_house.adapter.output.recommendation_agent import (
    StudentHouseRecommendationAgent,
)
from modules.student_house.infrastructure.repository.student_house_embedding_search_repository import \
    StudentHouseEmbeddingSearchRepository
from modules.student_house.infrastructure.repository.student_house_search_repository import StudentHouseSearchRepository


load_dotenv()

AMQP_HOST = os.getenv("AMQP_HOST")
AMQP_PORT = int(os.getenv("AMQP_PORT", "5672"))
AMQP_USER = os.getenv("AMQP_USER")
AMQP_PASSWORD = os.getenv("AMQP_PASSWORD")

QUEUE_NAME = "search.house.request"

def start_search_house_consumer():
    """
    RabbitMQ Consumer 엔트리포인트
    - 메시지를 받아 UseCase로 위임
    """
    credentials = pika.PlainCredentials(
        AMQP_USER,
        AMQP_PASSWORD,
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=AMQP_HOST,
            port=AMQP_PORT,
            credentials=credentials,
        )
    )

    channel = connection.channel()

    # 큐 선언 (Producer와 반드시 동일)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # 한 번에 하나씩만 처리 (AI 작업 보호)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        """
        MQ 메시지 수신 콜백
        """
        payload = json.loads(body)
        search_house_id = payload["search_house_id"]

        db = next(get_db_session())

        # 의존성 생성 (router와 동일)
        finder_request_repo = FinderRequestRepository(db)
        embedding_repo = FinderRequestEmbeddingRepository()
        search_repo = StudentHouseSearchRepository()
        vector_repo = StudentHouseEmbeddingSearchRepository()
        embedder = OpenAIEmbeddingAgent()

        usecase = RecommendStudentHouseUseCase(
            finder_request_repo,
            embedding_repo,
            search_repo,
            vector_repo,
            embedder,
        )

        ai_agent = StudentHouseRecommendationAgent(usecase)

        usecase = ProcessSearchHouseUseCase(db, ai_agent)

        try:
            usecase.execute(search_house_id)
            # 모든 처리가 끝났을 때 ACK
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            # 실패해도 ACK (무한 재시도 방지)
            print(f"[ERROR] search_house_id={search_house_id}, error={e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        finally:
            db.close()

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
    )

    print("[Consumer] search_house consumer started")
    channel.start_consuming()

if __name__ == "__main__":
    start_search_house_consumer()