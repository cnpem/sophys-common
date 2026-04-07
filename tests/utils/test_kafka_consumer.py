from datetime import datetime, timezone

from kafka.producer import KafkaProducer
from kafka.consumer import KafkaConsumer
from kafka.structs import TopicPartition

import numpy as np

from ophyd.sim import hw
from bluesky import plans as bp

from sophys.common.utils.kafka.monitor import seek_start_document, seek_back_in_time


def test_seek_start(
    kafka_producer: KafkaProducer,
    kafka_consumer: KafkaConsumer,
    kafka_topic,
    run_engine_without_md,
):
    partition_number = list(kafka_consumer.partitions_for_topic(kafka_topic))[0]
    topic_partition = TopicPartition(kafka_topic, partition_number)
    original_offset = kafka_consumer.position(topic_partition)

    uid, *_ = run_engine_without_md(bp.count([hw().det], num=10))

    def seek_and_assert_positions(offset: int, seeked_event_name: str):
        kafka_consumer.seek(topic_partition, offset)

        record = kafka_consumer.poll(
            timeout_ms=1_000, max_records=1, update_offsets=False
        )[topic_partition][0]

        event_name, _ = record.value
        assert event_name == seeked_event_name

        seek_start_document(kafka_consumer, record)

        record = kafka_consumer.poll(
            timeout_ms=1_000, max_records=1, update_offsets=False
        )[topic_partition][0]

        event_name, _ = record.value
        assert event_name == "start"

    kafka_producer.flush(timeout=1.0)
    while kafka_consumer.poll(timeout_ms=100) != {}:
        pass

    new_offset = kafka_consumer.position(topic_partition)
    # start (1) + descriptor (1) + events (10) + stop (1)
    assert new_offset - original_offset == 13

    # From stop to start
    seek_and_assert_positions(new_offset - 1, "stop")

    # From start to start (do nothing)
    seek_and_assert_positions(original_offset, "start")

    # From event in the middle to start
    seek_and_assert_positions(original_offset + 5, "event")

    # From descriptor to start
    seek_and_assert_positions(original_offset + 1, "descriptor")


def test_seek_back_in_time(
    kafka_producer: KafkaProducer,
    kafka_consumer: KafkaConsumer,
    kafka_topic,
    run_engine_without_md,
):
    partition_number = list(kafka_consumer.partitions_for_topic(kafka_topic))[0]
    topic_partition = TopicPartition(kafka_topic, partition_number)

    kafka_consumer.seek_to_beginning()
    oldest_offset = kafka_consumer.position(topic_partition)

    kafka_consumer.seek_to_end()
    newest_offset = kafka_consumer.position(topic_partition)

    if newest_offset - oldest_offset < 5:
        # Add some new time-spaced data.
        for _ in range(5):
            run_engine_without_md(bp.count([hw().det], num=2, delay=1))
        while kafka_consumer.poll(timeout_ms=100) != {}:
            pass
        newest_offset = kafka_consumer.position(topic_partition)

    offsets = [round(x) for x in np.linspace(oldest_offset, newest_offset - 1, num=5)]
    timestamps = list()
    for offset in offsets:
        kafka_consumer.seek(topic_partition, offset)

        record = kafka_consumer.poll(
            timeout_ms=1_000, max_records=1, update_offsets=False
        )[topic_partition][0]
        timestamps.append(record.timestamp // 1000)

    for expected_timestamp in timestamps:
        time_delta = datetime.now(timezone.utc) - datetime.fromtimestamp(
            expected_timestamp, tz=timezone.utc
        )
        seek_back_in_time(kafka_consumer, time_delta)

        record = kafka_consumer.poll(
            timeout_ms=1_000, max_records=1, update_offsets=False
        )[topic_partition][0]

        assert np.isclose(record.timestamp // 1000, expected_timestamp, atol=1)
