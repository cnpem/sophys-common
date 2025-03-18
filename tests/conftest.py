import queue

import pytest

import msgpack
import msgpack_numpy as _m

from kafka.producer import KafkaProducer

from bluesky import RunEngine

from sophys.common.utils.kafka.monitor import ThreadedMonitor

_m.patch()


@pytest.fixture(scope="session")
def kafka_bootstrap_ip():
    return "localhost:9092"


@pytest.fixture(scope="session")
def kafka_topic():
    return "test_bluesky_raw_docs"


@pytest.fixture(scope="function")
def save_queue_size() -> int:
    return 4


@pytest.fixture(scope="function")
def _save_queue(save_queue_size) -> queue.Queue:
    return queue.Queue(save_queue_size)


@pytest.fixture(scope="function")
def save_queue(_save_queue) -> queue.Queue:
    """_save_queue, but emptying the Queue everytime."""
    while not _save_queue.empty():
        _save_queue.get_nowait()
    return _save_queue


@pytest.fixture(scope="function")
def error_queue_size() -> int:
    return 4


@pytest.fixture(scope="function")
def _error_queue(error_queue_size) -> queue.Queue:
    return queue.Queue(error_queue_size)


@pytest.fixture(scope="function")
def error_queue(_error_queue) -> queue.Queue:
    """_error_queue, but emptying the Queue everytime."""
    while not _error_queue.empty():
        _error_queue.get_nowait()
    return _error_queue


@pytest.fixture(scope="function")
def _incomplete_documents():
    return list()


@pytest.fixture(scope="function")
def incomplete_documents(_incomplete_documents):
    """_incomplete_documents, but emptying the list everytime."""
    while len(_incomplete_documents) > 0:
        _incomplete_documents.remove(_incomplete_documents[0])
    return _incomplete_documents


@pytest.fixture(scope="function")
def kafka_producer(kafka_bootstrap_ip):
    producer = KafkaProducer(
        bootstrap_servers=[kafka_bootstrap_ip], value_serializer=msgpack.dumps
    )
    yield producer
    producer.flush()
    producer.close()


@pytest.fixture(scope="function")
def base_md(tmp_path_factory):
    return {
        "metadata_save_file_location": str(tmp_path_factory.mktemp("metadata")),
        "metadata_save_file_identifier": "test_metadata",
    }


@pytest.fixture(scope="function")
def run_engine_with_md(base_md, kafka_producer, kafka_topic):
    RE = RunEngine(base_md)
    RE.subscribe(lambda name, doc: kafka_producer.send(kafka_topic, (name, doc)))
    return RE


@pytest.fixture(scope="function")
def run_engine_without_md(kafka_producer, kafka_topic):
    RE = RunEngine()
    RE.subscribe(lambda name, doc: kafka_producer.send(kafka_topic, (name, doc)))
    return RE


@pytest.fixture(scope="function")
def good_monitor(save_queue, incomplete_documents, kafka_topic) -> ThreadedMonitor:
    mon = ThreadedMonitor(save_queue, incomplete_documents, kafka_topic, "test")
    mon.start()

    mon.running.wait(timeout=2.0)

    return mon
