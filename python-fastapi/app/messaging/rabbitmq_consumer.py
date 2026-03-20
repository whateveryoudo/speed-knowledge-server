import aio_pika
from app.core.config import settings
import json
import asyncio
from app.messaging.handlers import ROUTES


def _retry_count_from_x_death(headers: dict | None) -> int:
    """获取重试次数"""
    if headers is None:
        return 0
    x_death = headers.get("x-death", [])
    if not x_death or not isinstance(x_death, list):
        return 0
    return sum(int(item.get("count", 0)) for item in x_death)


async def _publish_to_dlq(
    message: aio_pika.IncomingMessage, exchange: aio_pika.Exchange, routing_key: str
):
    """发布到死信队列"""
    msg = aio_pika.Message(
        body=message.body,
        headers=message.headers,
        content_type=message.content_type,
        content_encoding=message.content_encoding,
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await exchange.publish(msg, routing_key=routing_key)


async def start_rabbitmq_consumer():
    """启动rabbitmq消费者"""

    main_exchange_name = settings.RABBITMQ_EXCHANGE
    main_routing_key = settings.RABBITMQ_ROUTING_KEY
    main_queue_name = settings.RABBITMQ_QUEUE
    retry_exchange_name = f"{main_exchange_name}.retry"
    dlq_exchange_name = f"{main_exchange_name}.dlq"

    retry_queue_name = getattr(
        settings, "RABBITMQ_RETRY_QUEUE", f"{main_queue_name}.retry"
    )
    dlq_queue_name = getattr(settings, "RABBITMQ_DLQ_QUEUE", f"{main_queue_name}.dlq")

    max_retries = getattr(settings, "RABBITMQ_MAX_RETRIES", 5)
    dlq_routing_key = getattr(
        settings, "RABBITMQ_DLQ_ROUTING_KEY", f"{main_routing_key}.dlq"
    )

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    try:
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=50)

            main_exchange = await channel.declare_exchange(
                settings.RABBITMQ_EXCHANGE,
                type=aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            retry_exchange = await channel.declare_exchange(
                retry_exchange_name, type=aio_pika.ExchangeType.TOPIC, durable=True
            )
            dlq_exchange = await channel.declare_exchange(
                dlq_exchange_name, type=aio_pika.ExchangeType.TOPIC, durable=True
            )

            main_queue = await channel.declare_queue(
                main_queue_name,
                durable=True,
                arguments={"x-dead-letter-exchange": retry_exchange_name},
            )
            retry_queue = await channel.declare_queue(
                retry_queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": main_exchange_name,
                    "x-message-ttl": settings.RABBITMQ_RETRY_DELAY_MS,
                },
            )
            dlq_queue = await channel.declare_queue(dlq_queue_name, durable=True)

            await main_queue.bind(main_exchange, routing_key=main_routing_key)
            await retry_queue.bind(retry_exchange, routing_key=main_routing_key)
            await dlq_queue.bind(dlq_exchange, routing_key=dlq_routing_key)
            try:
                async with main_queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        try:
                            retry_count = _retry_count_from_x_death(message.headers)

                            try:
                                data = json.loads(message.body)
                            except Exception:
                                await _publish_to_dlq(
                                    message, dlq_exchange, dlq_routing_key
                                )
                                await message.ack()
                                continue
                            try:
                                handler = ROUTES.get(message.routing_key)
                                await handler(data)
                                # 处理消息
                                await message.ack()
                            except asyncio.CancelledError:
                                raise
                            except Exception as e:
                                print(f"处理消息时发生错误: {e}")
                                if retry_count >= max_retries:
                                    await _publish_to_dlq(
                                        message, dlq_exchange, dlq_routing_key
                                    )
                                    await message.ack()
                                else:
                                    await message.reject(requeue=False)

                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            # 兜底：避免消费者整个挂掉；这里一般也选择 reject 进 retry
                            await message.reject(requeue=False)
            except asyncio.CancelledError:
                # 允许外部优雅停止
                raise
    except Exception as e:
        print(f"启动消费者时发生错误: {e}")
        raise
