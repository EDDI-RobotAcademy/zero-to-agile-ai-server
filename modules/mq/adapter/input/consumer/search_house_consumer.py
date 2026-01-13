import json
import time
import os
from dotenv import load_dotenv
import pika
import traceback

print("[consumer] file loaded")

from infrastructure.db.postgres import get_db_session
from modules.mq.adapter.output.repository.search_house_repository import SearchHouseRepository
from modules.recommendations.application.usecase.recommend_student_house import RecommendStudentHouseUseCase


# --- 의존성 추가 ---
# from modules.finder_request.adapter.output.repository.finder_request_repository import FinderRequestRepository
# from modules.house_platform.adapter.output.repository.house_platform_repository import HousePlatformRepository
# from modules.student_house_decision_policy.adapter.output.repository.student_house_score_repository import StudentHouseScoreRepository
# from modules.decision_context_signal_builder.adapter.output.repository.observation_repository import StudentRecommendationFeatureObservationRepository
# from modules.recommendations.application.usecase.recommend_student_house import RecommendStudentHouseUseCase




load_dotenv()

AMQP_HOST = os.getenv("AMQP_HOST")
AMQP_PORT = int(os.getenv("AMQP_PORT", "5672"))
AMQP_USER = os.getenv("AMQP_USER")
AMQP_PASSWORD = os.getenv("AMQP_PASSWORD")

QUEUE_NAME = "search.house.request"
EXCHANGE_NAME = "recommend.exchange"
ROUTING_KEY = "recommend.house"


def connect_with_retry(host, user, password, retry=20, delay=2):
    creds = pika.PlainCredentials(user, password)
    params = pika.ConnectionParameters(
        host=host,
        port=AMQP_PORT,
        credentials=creds,
    )
    for i in range(retry):
        try:
            print(f"[consumer] connecting... {i + 1}/{retry}")
            return pika.BlockingConnection(params)
        except Exception as e:
            print(f"[consumer] waiting MQ... {e}")
            time.sleep(delay)

    raise Exception("RabbitMQ not reachable after retries")


def start_search_house_consumer():
    connection = connect_with_retry(
        AMQP_HOST,
        AMQP_USER,
        AMQP_PASSWORD,
        retry=60,
        delay=2,
    )

    channel = connection.channel()
    print(f"[consumer] connected to MQ host={AMQP_HOST} queue={QUEUE_NAME}")

    # EXCHANGE 선언
    print("[consumer] declaring exchange...")
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True,
    )
    print("[consumer] exchange declared")

    # 큐 선언
    print("[consumer] declaring queue...")
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    print("[consumer] queue declared")

    # 큐 바인딩
    print("[consumer] binding queue to exchange...")
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY,
    )
    print("[consumer] queue bound")

    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        print(f"[consumer][callback] raw_body={body}")
        payload = json.loads(body)
        search_house_id = payload["search_house_id"]
        print(f"[consumer][search_house] Received search_house_id={search_house_id}")

        db = next(get_db_session())
        search_house_repo = SearchHouseRepository(db)

        try:
            finder_request_id = search_house_repo.get_finder_request_id_by_id(search_house_id)
            print(f"[consumer][callback] mapped {search_house_id} -> finder_request_id={finder_request_id}")

            ai_agent = RecommendStudentHouseUseCase()
            result_json = ai_agent.execute(finder_request_id)
            print(f"[consumer][callback] recommend result received {result_json}")

            search_house_repo.save_result(search_house_id, result_json)
            print("[consumer][callback] saved result successfully")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[ERROR][consumer][callback] search_house_id={search_house_id}, error={e}")
            traceback.print_exc()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        finally:
            print("[consumer][callback] closing DB session")
            db.close()

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
    )

    print("[consumer] start_consuming() now...")
    print("[Consumer] search.house.request consuming start")
    channel.start_consuming()


if __name__ == "__main__":
    start_search_house_consumer()