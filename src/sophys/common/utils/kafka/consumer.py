from datetime import datetime, timedelta, timezone, tzinfo

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from kafka.structs import TopicPartition


def seek_start_document(consumer: KafkaConsumer, record: ConsumerRecord):
    """
    Attempt to seek into the start document of the current run, based on data from the last received document.
    """
    topic_partition = TopicPartition(record.topic, record.partition)

    offset = record.offset
    event_name, event_data = record.value

    beginning_offset = consumer.beginning_offsets([topic_partition])[topic_partition]
    while event_name != "start" and offset != beginning_offset:
        if "seq_num" in event_data:
            offset = offset - event_data["seq_num"] - 1
        else:
            offset -= 1
        consumer.seek(topic_partition, offset)

        records = consumer.poll(timeout_ms=5_000, max_records=1, update_offsets=False)
        assert (
            topic_partition in records
        ), "Could not retrieve data from Kafka in seek_start."

        event_name, event_data = records[topic_partition][0].value


def seek_back_in_time(
    consumer: KafkaConsumer,
    rewind_time: timedelta,
    server_timezone: tzinfo = timezone.utc,
):
    """
    Rewind the consumer by 'rewind_time', up to the beginning offset.
    """
    now = datetime.now(server_timezone)

    all_partitions = [
        TopicPartition(topic_name, p)
        for topic_name in consumer.subscription()
        for p in consumer.partitions_for_topic(topic_name)
    ]

    # NOTE: offsets_for_times expects timestamps in ms, so we multiply by 1000.
    rewind_timestamp = int((now - rewind_time).timestamp() * 1000)
    timestamp_offsets = consumer.offsets_for_times(
        {p: rewind_timestamp for p in all_partitions}
    )

    for partition, offset_ts in timestamp_offsets.items():
        if offset_ts is not None:
            consumer.seek(partition, offset_ts.offset)
