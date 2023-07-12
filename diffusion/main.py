import asyncio
from multiprocessing import Process

from diffusion.consumer import AIOConsumer
from diffusion.process import Processor
from settings import model_names, KAFKA_CONSUMER_CONFIG


async def start_consumer(model_name):
    """
    This function initializes a AIOConsumer instance and
    a Processor instance which performs prompt guided Img2Img on message arrival
    :param model_name:
    :return:
    """
    handler = Processor(model_name)
    model_name = model_name.replace('/', '.')
    consumer = AIOConsumer({**KAFKA_CONSUMER_CONFIG, "group.id": model_name}, topic_handlers={model_name: handler})
    await consumer.poll()


def start_consumer_process(model_name):
    """
    This function was written only to support async
    :param model_name: Name of the model from huggingface
    :return:
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_consumer(model_name))
    finally:
        loop.close()


def run():
    """
    This function creates a process for each provided model
    :return:
    """
    processes = {}
    for model_name in model_names:
        p = Process(target=start_consumer_process, args=(model_name,))
        p.start()
        processes[model_name] = p


if __name__ == '__main__':
    run()
