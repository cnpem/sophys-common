import pytest

import queue
import time

import msgpack
import msgpack_numpy as _m

from kafka.producer import KafkaProducer
from kafka.consumer import KafkaConsumer
from kafka.structs import TopicPartition

from ophyd.sim import hw
from bluesky import RunEngine, plans as bp, plan_stubs as bps, preprocessors as bpp

from sophys.common.utils.kafka.monitor import ThreadedMonitor

from . import _wait


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
def kafka_consumer(kafka_bootstrap_ip, kafka_topic):
    consumer = KafkaConsumer(
        bootstrap_servers=[kafka_bootstrap_ip], value_deserializer=msgpack.unpackb
    )

    # Connect the consumer properly to the topic
    partition = TopicPartition(kafka_topic, 0)
    consumer.assign([partition])
    print("Starting offset:")
    # Fun fact: this is actually required for the tests to work properly,
    # because otherwise it doesn't update the current offset before the
    # producer starts throwing events at the topic. :)))))
    print(consumer.position(partition))

    return consumer


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


#
# Tests
#


def test_kafka_topic(good_monitor, kafka_topic):
    assert good_monitor.topic() == kafka_topic


def test_kafka_properly_configured(kafka_producer, kafka_consumer, kafka_topic):
    kafka_producer.send(kafka_topic, ("start", {"uid": "1234"}))
    records = kafka_consumer.poll(timeout_ms=5_000)
    assert len(records) != 0, "Failed to retrieve any data from the topic."

    partition = list(kafka_consumer.assignment())[0]
    event = records[partition][0].value

    assert event[0] == "start"
    assert isinstance(event[1], dict)
    assert event[1]["uid"] == "1234"


def test_start_stop(good_monitor, kafka_topic, kafka_producer, incomplete_documents):
    _wait(lambda: "1234" not in incomplete_documents)
    kafka_producer.send(kafka_topic, ("start", {"uid": "1234"}))
    kafka_producer.flush()
    _wait(lambda: "1234" in incomplete_documents)
    kafka_producer.send(kafka_topic, ("stop", {"uid": "5678", "run_start": "1234"}))
    kafka_producer.flush()
    _wait(lambda: "1234" not in incomplete_documents)


def test_basic_plan(
    good_monitor, run_engine_without_md, incomplete_documents, save_queue: queue.Queue
):
    uid, *_ = run_engine_without_md(bp.count([hw().det], num=1))

    _wait(lambda: uid not in incomplete_documents)

    assert save_queue.get(True, timeout=2.0) is not None


def test_basic_plan_overflowing_save_queue(
    good_monitor,
    run_engine_without_md,
    incomplete_documents,
    save_queue: queue.Queue,
    save_queue_size,
):
    _hw = hw()
    for _ in range(save_queue_size):
        uid, *_ = run_engine_without_md(bp.count([_hw.det], num=1))

        _wait(lambda: uid not in incomplete_documents)

    # Should be in incomplete_documents until we take from the save queue
    uid_1, *_ = run_engine_without_md(bp.count([_hw.det], num=1))

    assert save_queue.get(True, timeout=2.0) is not None
    assert save_queue.get(True, timeout=2.0) is not None

    assert uid_1 in incomplete_documents

    # We need to do another run to add everything to the queue
    uid_2, *_ = run_engine_without_md(bp.count([_hw.det], num=1))

    # Now both should be added
    _wait(lambda: uid_1 not in incomplete_documents)
    _wait(lambda: uid_2 not in incomplete_documents)


def test_concurrent_plan_overflowing_save_queue(
    good_monitor,
    run_engine_without_md,
    incomplete_documents,
    save_queue: queue.Queue,
    save_queue_size,
):
    _hw = hw()
    uids = []
    for _ in range(save_queue_size):
        uid, *_ = run_engine_without_md(bp.count([_hw.det], num=10))
        uids.append(uid)

    for uid in uids:
        _wait(lambda: uid not in incomplete_documents)
    time.sleep(1.0)

    # Should be in incomplete_documents until we take from the save queue
    uid_1, *_ = run_engine_without_md(bp.count([_hw.det], num=1))

    assert save_queue.get(True, timeout=2.0) is not None
    assert save_queue.get(True, timeout=2.0) is not None

    assert uid_1 in incomplete_documents

    # We need to do another run to add everything to the queue
    uid_2, *_ = run_engine_without_md(bp.count([_hw.det], num=1))

    # Now both should be added
    _wait(lambda: uid_1 not in incomplete_documents)
    _wait(lambda: uid_2 not in incomplete_documents)


def test_basic_plan_with_save_metadata(
    good_monitor, run_engine_with_md, incomplete_documents, save_queue: queue.Queue
):
    uid, *_ = run_engine_with_md(bp.count([hw().det], num=1))

    _wait(lambda: uid not in incomplete_documents)

    assert save_queue.get(True, timeout=2.0) is not None


def test_basic_custom_plan(
    good_monitor, run_engine_without_md, incomplete_documents, save_queue: queue.Queue
):
    def custom_plan():
        det = hw().det
        yield from bps.open_run({})
        yield from bps.declare_stream(det, name="primary")
        yield from bps.create()
        yield from bps.read(det)
        yield from bps.save()
        yield from bps.close_run("success")

    uid, *_ = run_engine_without_md(custom_plan())

    _wait(lambda: uid not in incomplete_documents)

    docs = save_queue.get(True, timeout=2.0)
    assert docs is not None

    # One start doc, one descriptor doc, one event doc, one stop doc
    assert len(docs) == 4, docs.get_raw_data()


def test_basic_fly_plan(
    good_monitor, run_engine_without_md, incomplete_documents, save_queue: queue.Queue
):
    def custom_plan():
        flyer = hw().flyer1
        yield from bp.fly([flyer])

    uid, *_ = run_engine_without_md(custom_plan())

    _wait(lambda: uid not in incomplete_documents)

    docs = save_queue.get(True, timeout=2.0)
    assert docs is not None

    # One start doc, one descriptor doc, twenty event doc (from 1 EventPage), one stop doc
    assert len(docs) == 23, docs.get_raw_data()


def test_basic_custom_plan_with_two_descriptor_documents(
    good_monitor, run_engine_without_md, incomplete_documents, save_queue: queue.Queue
):
    _hw = hw()
    det = _hw.det
    noisy_det = _hw.noisy_det

    @bpp.baseline_decorator([noisy_det])
    def custom_plan():
        yield from bps.open_run({})
        yield from bps.declare_stream(det, name="primary")
        yield from bps.create()
        yield from bps.read(det)
        yield from bps.save()
        yield from bps.close_run("success")

    uid, *_ = run_engine_without_md(custom_plan())

    _wait(lambda: uid not in incomplete_documents)

    docs = save_queue.get(True, timeout=2.0)
    assert docs is not None

    # One start doc, two descriptor doc, three event doc, one stop doc
    assert len(docs) == 7, docs.get_raw_data()


def test_basic_custom_plan_with_two_nested_runs(
    good_monitor, run_engine_without_md, incomplete_documents, save_queue: queue.Queue
):
    _hw = hw()
    det = _hw.det

    def custom_plan():
        yield from bps.open_run({})
        yield from bps.declare_stream(det, name="primary")
        yield from bps.create()
        yield from bps.read(det)
        yield from bps.save()
        yield from bpp.set_run_key_wrapper(bp.count([det], num=2), "inner")
        yield from bps.close_run("success")

    uid, *_ = run_engine_without_md(custom_plan())

    _wait(lambda: uid not in incomplete_documents)

    docs = save_queue.get(True, timeout=2.0)
    assert docs is not None

    # One start doc, one descriptor doc, two event doc, one stop doc
    assert len(docs) == 5, docs.get_raw_data()

    docs = save_queue.get(True, timeout=2.0)
    assert docs is not None

    # One start doc, one descriptor doc, one event doc, one stop doc
    assert len(docs) == 4, docs.get_raw_data()
