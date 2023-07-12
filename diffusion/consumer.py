import asyncio
import json
import logging
from time import sleep

import confluent_kafka
from confluent_kafka import KafkaException, KafkaError


class AIOConsumer:
    """
    Simple Kafka consumer class for pooling and processing messages.
    """
    def __init__(self, configs, topic_handlers, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._consumer = confluent_kafka.Consumer(configs)
        subscribed = False
        while not subscribed:
            logging.info(msg='Subscribing to topic')
            try:
                self._consumer.subscribe(list(topic_handlers.keys()))
                subscribed = True
            except KafkaException as e:
                logging.warning(msg=f"Couldn't subscribe to topic - {e}")
                sleep(10)
        self.topic_handlers = topic_handlers

    async def poll(self):
        try:
            while True:
                msg = self._consumer.poll()
                if msg is None:
                    continue
                print('New message arrived')
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print('%% %s [%d] reached end at offset %d\n' % (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error().UNKNOWN_TOPIC_OR_PART:
                        pass
                    else:
                        print(msg.error().code())
                        raise KafkaException(msg.error())
                elif msg.value():
                    handler = self.topic_handlers[str(msg.topic())]
                    await handler(json.loads(msg.value()))
        finally:
            self._consumer.close()
        return None
