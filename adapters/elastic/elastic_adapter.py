from elasticsearch import Elasticsearch

class ElasticAdaptor():
    def __init__(self):
        self.client = Elasticsearch(hosts=["elasticsearch:9200"])


if __name__ == '__main__':
    es = ElasticAdaptor()
    es.client.create(index='emran', body={"name":"ali"},id = 'test2')

