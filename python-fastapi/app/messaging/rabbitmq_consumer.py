import aio_pika
from app.core.config import settings
import json


async def start_rabbitmq_consumer():
    """启动rabbitmq消费者"""
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=50)

        exchange = await channel.declare_exchange(
            settings.RABBITMQ_EXCHANGE, type=aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(settings.RABBITMQ_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=settings.RABBITMQ_ROUTING_KEY)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(requeue=True):
                    data = json.loads(message.body)
                    print(data)
