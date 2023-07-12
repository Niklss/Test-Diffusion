import asyncio
from threading import Thread

import confluent_kafka
from confluent_kafka import KafkaException


class AIOProducer:
    """
    Simple async producer
    """
    def __init__(self, configs, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread()
        self._poll_thread.start()

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value):
        """
        Produce a message in a desired topic
        :param topic: Name of the topic
        :param value: json object
        :return:
        """
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)

        self._producer.produce(topic, value, on_delivery=ack)
        return result
