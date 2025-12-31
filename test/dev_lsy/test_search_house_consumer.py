import json
from unittest.mock import MagicMock, patch

import pytest

# 테스트 대상 함수 import
from modules.mq.adapter.input.consumer.search_house_consumer import (
    start_search_house_consumer,
)


def test_search_house_consumer_callback_executes_usecase_and_ack():
    """
    목적:
    - MQ 메시지 수신 시
    - ProcessSearchHouseUseCase.execute(search_house_id)가 호출되고
    - 메시지가 ack 되는지 검증
    """

    fake_search_house_id = 83
    fake_body = json.dumps({"search_house_id": fake_search_house_id}).encode()

    # --- pika channel / method mock ---
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = "test-tag"

    # --- pika connection / channel mock ---
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel

    # channel.basic_consume 에서 등록되는 callback을 잡기 위한 변수
    registered_callback = {}

    def fake_basic_consume(queue, on_message_callback):
        registered_callback["callback"] = on_message_callback

    mock_channel.basic_consume.side_effect = fake_basic_consume

    # --- UseCase mock ---
    with patch(
        "modules.mq.adapter.input.consumer.search_house_consumer.pika.BlockingConnection",
        return_value=mock_connection,
    ), patch(
        "modules.mq.adapter.input.consumer.search_house_consumer.ProcessSearchHouseUseCase"
    ) as mock_process_usecase, patch(
        "modules.mq.adapter.input.consumer.search_house_consumer.get_db_session"
    ) as mock_get_db_session:

        # fake db session
        fake_db = MagicMock()
        mock_get_db_session.return_value = iter([fake_db])

        # usecase 인스턴스 mock
        mock_usecase_instance = MagicMock()
        mock_process_usecase.return_value = mock_usecase_instance

        # --- consumer 시작 (note: start_consuming은 실제로 돌리지 않음) ---
        with patch.object(mock_channel, "start_consuming"):
            start_search_house_consumer()

        # --- 등록된 callback 실행 ---
        callback = registered_callback["callback"]
        callback(
            ch=mock_channel,
            method=mock_method,
            body=fake_body,
        )

        # --- 검증 ---
        mock_process_usecase.assert_called_once()
        mock_usecase_instance.execute.assert_called_once_with(fake_search_house_id)
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag=mock_method.delivery_tag
        )