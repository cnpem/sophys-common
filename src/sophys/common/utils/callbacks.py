import typing


def make_kafka_callback(
    topic_names: typing.Union[str, typing.List[str]],
    bootstrap_servers: typing.Optional[
        typing.Union[str, typing.List[str]]
    ] = "localhost:9092",
    backoff_times: typing.Optional[typing.List[float]] = [0.1, 1.0, 5.0, 20.0, 60.0],
):
    """
    Create a Bluesky document callback, that sends the data created by the RunEngine
    to one or more Kafka topics, encoded in msgpack.

    Parameters
    ----------
    topic_names : list of str
        A list of topic names to send the data to.
    bootstrap_servers : list of str, optional
        A list of IPs / hosts to check for the specified topics. Defaults to ``localhost:9092``.
    backoff_times : list of float, optional
        A list of times, in seconds, to delay each successive attempt at connecting to a Kafka broker.

        If a connection fails, it will be retried ``len(backoff_times)`` times, sleeping for ``backoff_times[i]``
        seconds between each attempt. If it reaches the end of the list, it will raise an Exception.

        Defaults to ``[0.1, 1.0, 5.0, 20.0, 60.0]``.
    """
    if not isinstance(topic_names, list):
        topic_names = [topic_names]
    if not isinstance(bootstrap_servers, list):
        bootstrap_servers = [bootstrap_servers]

    import time

    # NOTE: These should be here so that not having the packages installed doesn't break a client that doesn't need them.
    from kafka import KafkaProducer
    from kafka.errors import NoBrokersAvailable
    from msgpack import dumps

    i = 0
    while True:
        try:
            __kafka_producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers, value_serializer=dumps
            )
            break
        except NoBrokersAvailable as _e:
            if i == len(backoff_times):
                raise _e
            time.sleep(backoff_times[i])
            i += 1

    def __callback(name, doc):
        for topic in topic_names:
            __kafka_producer.send(topic, (name, doc))

    return __callback
