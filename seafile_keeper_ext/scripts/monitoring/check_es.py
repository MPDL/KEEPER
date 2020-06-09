#!/usr/bin/python3
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200/'])

if not es.ping():
    print("CRITICAL: Cannot connect to elasticsearch")
    exit(2)

health = es.cluster.health()

if health['status'] == 'green':
    print("OK")
    exit(0)

if health['status'] == 'yellow':
    print("WARNING:", health)
    exit(1)

if health['status'] == 'red':
    print("CRITICAL:", health)
    exit(2)
