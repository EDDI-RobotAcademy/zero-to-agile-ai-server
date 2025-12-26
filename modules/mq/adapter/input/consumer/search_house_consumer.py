import json
import pika
from modules.mq.application.usecase.process_search_house_usecase import ProcessSearchHouseUseCase
import os
from dotenv import load_dotenv
from infrastructure.db.postgres import get_db_session  # Import DB session factory used by FastAPI router

# 아직 에이전트 로직 없어서 가라 로직 #
class AiAgent:
    def __init__(self):
        pass

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

    def callback(ch, method, body):
        """
        MQ 메시지 수신 콜백
        """
        payload = json.loads(body)
        search_house_id = payload["search_house_id"]

        db = next(get_db_session())

        #ai_agent = HouseRecommendationAgent(...)
        ai_agent = AiAgent()

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