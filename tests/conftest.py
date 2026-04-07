import pytest

import msgpack_numpy as msgpack

from kafka import KafkaConsumer, KafkaProducer

from bluesky import RunEngine

from .soft_ioc import start_soft_ioc


@pytest.fixture(scope="session")
def soft_ioc():
    soft_ioc_prefix, stop_soft_ioc = start_soft_ioc()
    yield soft_ioc_prefix
    stop_soft_ioc()


@pytest.fixture(scope="session")
def kafka_bootstrap_ip():
    return "localhost:9092"


@pytest.fixture(scope="session")
def kafka_topic():
    return "test_bluesky_raw_docs"


@pytest.fixture(scope="function")
def kafka_producer(kafka_bootstrap_ip):
    producer = KafkaProducer(
        bootstrap_servers=[kafka_bootstrap_ip], value_serializer=msgpack.dumps
    )
    yield producer
    producer.flush()
    producer.close()


@pytest.fixture(scope="function")
def kafka_consumer(kafka_bootstrap_ip, kafka_topic):
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=[kafka_bootstrap_ip],
        value_deserializer=msgpack.unpackb,
    )

    # Connect the consumer properly to the topic
    consumer.poll(timeout_ms=100, max_records=1, update_offsets=False)

    return consumer


@pytest.fixture(scope="function")
def run_engine_without_md(kafka_producer, kafka_topic):
    RE = RunEngine()
    RE.subscribe(lambda name, doc: kafka_producer.send(kafka_topic, (name, doc)))
    return RE
