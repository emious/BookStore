from adapters.kafka.kafka_adapter import KafkaAdapter
from adapters.elastic.elastic_adapter import ElasticAdaptor
kafka = KafkaAdapter()
elastic = ElasticAdaptor()
while True:
    message_list  = kafka.consume_kafka(topic='log', consumer_group='elastic')
    for dict_body in message_list:
        action_datetime = dict_body.get("action_datetime")
        # ElasticAdaptor().client.create(index='log',body=dict_body,id=action_datetime)
        elastic.client.index(index='log',body=dict_body,id=action_datetime)
        print("logged to elastic")
