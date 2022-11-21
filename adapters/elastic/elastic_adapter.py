from elasticsearch import Elasticsearch

class ElasticAdaptor():
    def __init__(self):
        self.client = Elasticsearch(hosts=["127.0.0.1:9200"])


if __name__ == '__main__':
    es = ElasticAdaptor()
    es.client.create(index='emran', body={"name":"ali"},id = 'test2')

