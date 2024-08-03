from confluent_kafka import Producer
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conf = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
    "client.id": "python-producer",
    "acks": "all",
}

producer = Producer(conf)


def delivery_report(err, msg):
    if err is not None:
        logger.error("Message delivery failed: {}".format(err))
    else:
        logger.info("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


def produce_message(topic, message):
    try:
        producer.produce(
            topic,
            key=(message["key"]),
            value=json.dumps(message),
            callback=delivery_report,
        )
        producer.flush()
    except Exception as e:
        logger.error("Failed to produce message: {}".format(e))
