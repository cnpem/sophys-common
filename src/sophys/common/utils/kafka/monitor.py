import logging
import json
from functools import wraps, partial
from typing import Optional

from threading import Thread
from queue import Full as QueueFullException, Queue

import msgpack_numpy as _m

from kafka import KafkaConsumer
from kafka.structs import TopicPartition

from event_model import EventPage, unpack_event_page


def _get_uid_from_event_data(event_data: dict):
    return event_data.get("uid", None)


def _get_uid_from_datum_data(datum_data: dict):
    return datum_data.get("datum_id", None)


def _get_resource_uid_from_datum_data(datum_data: dict):
    return datum_data.get("resource", None)


def _get_descriptor_uid_from_event_data(event_data: dict):
    return event_data.get("descriptor", None)


def _get_start_uid_from_event_data(event_data: dict):
    # TODO: Deal with non stop documents.
    return event_data.get("run_start", None)


class DocumentDictionary(dict):
    """Auxiliary class for accumulating Document entries."""

    @wraps(dict.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger("DocumentDictionary")

        self._original_stream = []

        self.__start_document_uid: str = None
        self.__descriptor_documents_uids: list[str] = []
        self.__stop_document_uid: str = None

        self.__subscriptions = []

    def subscribe(self, fn: callable):
        """
        Subscribe `fn` to be notified (called) whenever a new entry is added.

        Parameters
        ----------
        fn : callable
            The function to be called, with signature (event_name: str, uuid: str) -> None.
        """
        self.__subscriptions.append(fn)

        if self.start_document is not None:
            fn("start", self.identifier)

    def clear_subscriptions(self):
        """Clear all subscriptions to this object."""
        self.__subscriptions = []

    def _run_subscriptions(self, event_name: str, event_uuid: str):
        for fn in self.__subscriptions:
            fn(event_name, event_uuid)

    def append(self, event_name: str, event_data: dict):
        """
        Add a new Document entry to this Dictionary.

        Parameters
        ----------
        event_name : str
            The event name, as specified in the Kafka event message.
        event_data : dict
            The event data, containing all the relevant event data, as defined by Bluesky's event model.
        """
        # Pre-filter EventPage documents into a series of Events.
        if event_name == "event_page":
            event_gen = unpack_event_page(EventPage(event_data))
            for event in event_gen:
                self.append("event", event)

            return

        self._logger.debug(
            "Appending data to DocumentDict: {} {}".format(event_name, event_data)
        )

        self._original_stream.append((event_name, event_data))

        # NOTE: Add extra key to all documents specifying its type,
        # to facilitate re-processing of saved files.
        event_data["document_type"] = event_name

        if (uid := _get_uid_from_event_data(event_data)) is not None:
            super().update({uid: event_data})
        elif (uid := _get_uid_from_datum_data(event_data)) is not None:
            # FIXME: Relate datum with their resource.
            super().update({uid: event_data})
        else:
            print("Invalid event data:")
            print(event_data)
            return

        if event_name == "start":
            self.__start_document_uid = uid
        elif event_name == "descriptor":
            # TODO: Validate the descriptor document's start_document's uid is what we think it is.
            self.__descriptor_documents_uids.append(uid)
        elif event_name == "stop":
            # TODO: Validate the stop document's descriptor_document's uid is what we think it is.
            self.__stop_document_uid = uid

        self._run_subscriptions(event_name, uid)

    def __repr__(self):
        return "DocumentDictionary ({})".format(self.identifier)

    def get_raw_data(self):
        """Returns a JSON-formatted string representing the contents of this dictionary."""
        return json.dumps(dict.__repr__(self))

    @classmethod
    def fromJSON(cls, path):
        """Create a DocumentDictionary from a JSON file."""

        data = None
        with open(path, "r") as _f:
            data = json.load(_f)

        obj = DocumentDictionary()

        for document_type, document in data:
            obj.append(document_type, document)

        return obj

    @property
    def identifier(self):
        """The run identifier, i.e. the name of the run maintained by this dictionary."""
        if self.start_document is None:
            self._logger.warning(
                "Calling 'indentifier' will return None, as there's no start document."
            )
            return None

        return self.__start_document_uid

    @property
    def start_document(self):
        return (
            self[self.__start_document_uid]
            if self.__start_document_uid is not None
            else None
        )

    @property
    def descriptor_documents(self):
        return [
            self[uid] for uid in self.__descriptor_documents_uids if uid is not None
        ]

    @property
    def stop_document(self):
        return (
            self[self.__stop_document_uid]
            if self.__stop_document_uid is not None
            else None
        )


class MultipleDocumentDictionary(dict):
    """
    A container for (potentially) multiple DocumentDictionarys.

    This exists solely to provide a way for us to use `__getitem__`
    when receiving raw data to get the relevant dictionary, while
    providing support for concurrent runs monitoring.
    """

    def append(self, data: tuple):
        # NOTE: Create a new dictionary here instead of clearing the old one,
        #       to avoid having to copy it when passing it onto the save queue.
        new_doc = DocumentDictionary()
        new_doc.append(*data)

        self[new_doc.identifier] = new_doc

    def find_with_descriptor(self, descriptor_uid):
        """Retrieve the UUID for a run dictionary containing the given descriptor."""
        for id, doc_dict in self.items():
            for desc_doc in doc_dict.descriptor_documents:
                if (
                    desc_doc is not None
                    and _get_uid_from_event_data(desc_doc) == descriptor_uid
                ):
                    return id

    def find_with_resource(self, resource_uid):
        """Retrieve the UUID for a run dictionary containing the given resource."""
        for id, doc_dict in self.items():
            for doc in doc_dict.values():
                if doc is not None and _get_uid_from_event_data(doc) == resource_uid:
                    return id

    def get_by_identifier(self, id: str):
        """
        Retrieve a DocumentDictionary with the given identifier.

        Parameters
        ----------
        id : str
            The identifier to search for.

        Raises
        ------
        KeyError
            The given identifier is not present in this container.
        """

        return super().__getitem__(id)

    def __getitem__(self, data: tuple):
        start_uid = _get_start_uid_from_event_data(data[1])
        if start_uid is not None:
            return super().__getitem__(start_uid)

        descriptor_uid = _get_descriptor_uid_from_event_data(data[1])
        if descriptor_uid is not None:
            return super().__getitem__(self.find_with_descriptor(descriptor_uid))

        uid = _get_uid_from_event_data(data[1])
        if uid is not None:
            return super().__getitem__(uid)

        resource_uid = _get_resource_uid_from_datum_data(data[1])
        if resource_uid is not None:
            return super().__getitem__(self.find_with_resource(resource_uid))


class MonitorBase(KafkaConsumer):
    def __init__(
        self,
        save_queue: Optional[Queue],
        incomplete_documents: list,
        topic_name: str,
        logger_name: str,
        **configs,
    ):
        """
        A KafkaConsumer that handles specifically Bluesky documents in msgpack format.

        Parameters
        ----------
        save_queue : queue.Queue, optional
            The queue in which to put complete DocumentDictionary items for saving.
            If None, all runs will be immediately discarted upon completion.
        incomplete_documents : list
            A list of all the incomplete (not submitted to the save queue) runs.
        topic_name : str
            The Kafka topic to monitor.
        logger_name : str, optional
            Name of the logger to use for info / debug during the monitor processing.
        **configs : dict or keyword arguments
            Extra arguments to pass to the KafkaConsumer's constructor.
        """
        super().__init__(topic_name, value_deserializer=_m.unpackb, **configs)

        self.name = repr(self)

        self.__documents = MultipleDocumentDictionary()
        self.__save_queue = save_queue

        self.__incomplete_documents = incomplete_documents
        self.__incomplete_documents_save_attempts = dict()

        self._logger = logging.getLogger(logger_name)

        self.__subscriptions = []

    def subscribe(self, fn: callable):
        """
        Subscribe `fn` to be notified (called) whenever a new entry is added to a DocumentDictionary.

        Parameters
        ----------
        fn : callable
            The function to be called, with signature (event_name: str, event_data: dict) -> None.
        """
        self.__subscriptions.append(fn)

    def clear_subscriptions(self):
        """Clear all subscriptions to this object."""
        self.__subscriptions = []

    def _run_subscriptions(self, run_uid: str, event_name: str, event_uuid: str):
        event_data = self.__documents.get_by_identifier(run_uid)[event_uuid]
        for fn in self.__subscriptions:
            fn(event_name, event_data)

    def __repr__(self):
        return "Monitor ({})".format(self.topic())

    def topic(self):
        """Get the name of the Kafka topic monitored by this object."""
        return "".join(self.subscription())

    def seek_start(
        self, topic: str, partition_id: int, offset: int, event_data: dict
    ) -> None:
        """Attempt to seek into the start document of the current run. May not seek if the current event does not have a sequence number."""
        if "seq_num" not in event_data:
            self._logger.debug(
                "Sequence numbers are not available! o.O\n {}".format(str(event_data))
            )
            # Hopefully a future event will have it!
            return
        self.seek(
            TopicPartition(topic, partition_id), offset - event_data["seq_num"] - 1
        )

    def handle_event(self, event):
        self._logger.debug("Event received.")
        try:
            data = event.value

            if len(data) != 2:
                self._logger.warning(
                    "Event data does not have two elements.\n {}".format(str(data))
                )
                return

            if data[0] == "start":
                self._logger.info("Received a 'start' document.")

                self.__documents.append(data)
                new_run_uid = self.__documents[data].identifier
                self.__incomplete_documents.append(new_run_uid)

                self.__documents[data].subscribe(
                    partial(self._run_subscriptions, new_run_uid)
                )

                return

            try:
                if len(self.__documents[data]) == 0:
                    # In the middle of a run, try to go back to the beginning
                    self.seek_start(event.topic, event.partition, event.offset, data[1])
                    return
            except KeyError:
                # In the middle of a run, try to go back to the beginning
                self.seek_start(event.topic, event.partition, event.offset, data[1])
                return

            self.__documents[data].append(*data)

            if data[0] == "stop":
                self._logger.info(
                    "Run '{}': Received a 'stop' document.".format(
                        self.__documents[data].identifier
                    )
                )

                self.__documents[data].clear_subscriptions()

                # TODO: Validate number of saved entries via the stop document's num_events
                # TODO: Validate successful run via the stop document's exit_status

                if self.__save_queue is None:
                    return

                # Save documents not yet saved.
                _completed_documents = list()
                for id in self.__incomplete_documents:
                    doc = self.__documents.get_by_identifier(id)
                    try:
                        self.__save_queue.put(doc, block=True, timeout=2.0)
                    except QueueFullException:
                        self._logger.warning(
                            "The save queue is full! Could not push the run '{}' unto it.".format(
                                id
                            )
                        )
                    except Exception as e:
                        self._logger.error(
                            "Unhandled exception while trying to save documents. Will try to continue regardless."
                        )
                        self._logger.error("Exception if you're into that:")
                        self._logger.exception(e)

                        if id in self.__incomplete_documents_save_attempts:
                            self.__incomplete_documents_save_attempts[id] += 1

                            if self.__incomplete_documents_save_attempts[id] >= 3:
                                self._logger.error(
                                    "Failed to save document with id '%s' three times. Giving up.",
                                    id,
                                )

                                self.__incomplete_documents.remove(id)
                                self.__documents.pop(id)
                                del self.__incomplete_documents_save_attempts[id]
                        else:
                            self.__incomplete_documents_save_attempts[id] = 1

                    else:
                        _completed_documents.append(id)

                for id in _completed_documents:
                    self.__incomplete_documents.remove(id)
                    self.__documents.pop(id)

                    if id in self.__incomplete_documents_save_attempts:
                        del self.__incomplete_documents_save_attempts[id]

        except Exception as e:
            self._logger.error("Unhandled exception. Will try to continue regardless.")
            self._logger.error("Exception if you're into that:")
            self._logger.exception(e)

    def run(self):
        """Start monitoring the Kafka topic."""
        while not self._closed:
            try:
                for event in self:
                    self.handle_event(event)
            except StopIteration:
                pass

        KafkaConsumer.close(self)

    def is_incomplete(self):
        """
        Returns whether the Document is complete (with both start and stop documents), or not.

        If it's incomplete, it means it's either parsing the stream contents, or waiting for new events from the current run to arrive.
        If it's complete, it's waiting for a new run to start.
        """
        return self.__incomplete_documents


class ThreadedMonitor(MonitorBase, Thread):
    def __init__(self, *args, daemon=True, **kwargs):
        """
        A threaded KafkaConsumer that handles specifically Bluesky documents in msgpack format.

        To start it, run the `start` method.

        Parameters
        ----------
        save_queue : queue.Queue
            The queue in which to put complete DocumentDictionary items for saving.
        incomplete_documents : list
            A list of all the incomplete (not submitted to the save queue) runs.
        topic_name : str
            The Kafka topic to monitor.
        logger_name : str, optional
            Name of the logger to use for info / debug during the monitor processing.
        daemon : bool, optional
            If True, start the thread as a daemon (will exit when the main programs does).
            Defaults to True.
        **configs : dict or keyword arguments
            Extra arguments to pass to the KafkaConsumer's constructor.
        """

        Thread.__init__(self, daemon=daemon)
        MonitorBase.__init__(self, *args, **kwargs)
