import json
import logging

import pika

from app.application.interfaces.message_publisher import IMessagePublisher


logger = logging.getLogger(__name__)


class RabbitMQPublisher(IMessagePublisher):
    """Publishes file jobs to a durable RabbitMQ queue.

    Messages are persistent, so a broker restart does not lose accepted jobs.
    """

    def __init__(self, url: str, queue_name: str):
        self.url = url
        self.queue_name = queue_name

    def publish_file_job(self, file_id: int) -> None:
        connection = pika.BlockingConnection(
            pika.URLParameters(self.url)
        )

        try:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=json.dumps({"file_id": file_id}).encode(),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=pika.DeliveryMode.Persistent
                )
            )
        finally:
            connection.close()


class LoggingPublisher(IMessagePublisher):
    """Used when no broker is configured (RABBITMQ_URL unset).

    The job is already stored with status 'uploaded', so a worker can pick it
    up later; this only records that nothing was sent to a queue.
    """

    def publish_file_job(self, file_id: int) -> None:
        logger.info(
            "No message broker configured; job %s left with status 'uploaded'",
            file_id
        )
