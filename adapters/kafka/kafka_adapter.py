import datetime
import json

from kafka import KafkaProducer
from kafka import KafkaConsumer

from adapters.elastic.elastic_adapter import ElasticAdaptor


class KafkaAdapter():
    def __init__(self):
        self.kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')

    def produce_to_kafka(self,topic,value):
        # byte_value = value.encode()
        value = json.dumps(value).encode('utf-8')
        self.kafka_producer.send(topic=topic, value=value)
        self.kafka_producer.flush()

    def consume_kafka(self,topic,consumer_group):
        kafka_consumer = KafkaConsumer(topic,
                                       group_id=consumer_group,bootstrap_servers='kafka:9092',max_poll_records = 1)

        message_list = list()

        for msg in kafka_consumer:
            message = msg.value
            message = message.decode("utf-8")
            dict_body = json.loads(message)
            message_list.append(dict_body)
            kafka_consumer.close()

        print("done")
        return message_list
            # action_datetime = dict_body.get("action_datetime")
            # ElasticAdaptor().client.create(index='log',body=dict_body,id=action_datetime)
