"""
Outbound Adapter (Messaging)
- MessageQueuePort 구현체
- RabbitMQ에 {search_house_id} 메시지 발행만 담당
"""

import json
import pika
from modules.mq.application.port.message_queue_port import MessageQueuePort


class RabbitMQProducer(MessageQueuePort):
    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        # MVP routing
        self.exchange = "recommend.exchange"
        self.exchange_type = "direct"
        self.queue = "search.house.request"
        self.routing_key = "recommend.house"

    def publish_search_house(self, search_house_id: int) -> None:
        """
        Producer Step 2:
        - 단일 메시지 발행
        - 성공하면 return (예외 발생 시 상위에서 처리)
        """
        credentials = pika.PlainCredentials(self.user, self.password)
        params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
        )

        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # 선언은 멱등(idempotent)이라 매번 호출해도 안전
        channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=True,
        )
        channel.queue_declare(queue=self.queue, durable=True)
        channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue,
            routing_key=self.routing_key,
        )

        body = json.dumps({"search_house_id": search_house_id})

        channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),  # persistent message
        )

        connection.close()