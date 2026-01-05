import json
import os
import threading
import time

import pika
import pytest
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.mq.adapter.input.consumer.search_house_consumer import (
    start_search_house_consumer,
)
from modules.mq.adapter.output.repository.search_house_repository import (
    SearchHouseRepository,
)

QUEUE_NAME = "search.house.request"


@pytest.mark.integration
def test_search_house_consumer_real_rabbitmq():
    """
    REAL consumer integration test (NO MOCK)
    - 실제 RabbitMQ 사용
    - 실제 consumer 실행
    - 실제 DB 상태 변경 검증
    """

    # 🔹 반드시 DB에 QUEUED 상태로 존재해야 함
    search_house_id = 83  # 테스트 전에 직접 만들어둔 값

    # 1️⃣ consumer 실행 (백그라운드)
    consumer_thread = threading.Thread(
        target=start_search_house_consumer,
        daemon=True,  # pytest 종료 시 같이 종료
    )
    consumer_thread.start()

    # consumer가 큐에 붙을 시간
    time.sleep(2)

    # 2️⃣ 실제 RabbitMQ로 메시지 발행 (producer 역할)
    credentials = pika.PlainCredentials(
        os.getenv("AMQP_USER"),
        os.getenv("AMQP_PASSWORD"),
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("AMQP_HOST"),
            port=int(os.getenv("AMQP_PORT", "5672")),
            credentials=credentials,
        )
    )

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    payload = json.dumps(
        {"search_house_id": search_house_id}
    ).encode()

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=payload,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()

    # 3️⃣ consumer 처리 대기
    # AI / 외부 API 포함되어 있으면 충분히 늘려야 함
    time.sleep(10)

    # 4️⃣ DB 결과 검증
    db: Session = next(get_db_session())
    repo = SearchHouseRepository(db)

    entity = repo.get_by_id(search_house_id)

    assert entity is not None
    assert entity.status in ("PROCESSING", "COMPLETED", "FAILED")

    db.close()