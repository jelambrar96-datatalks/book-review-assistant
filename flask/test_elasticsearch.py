import unittest
import json

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


RAG_PROMPT = """
Imagine you’ve just finished reading the Harry Potter series, filled with magic,
friendship, and thrilling adventures. Now, I’d love to hear your thoughts!
Could you write a detailed review of the series, focusing on the following:

- Which book was your favorite and why?
- How did the character development of Harry, Hermione, and Ron impact your reading experience?
- What did you think of the magical world J.K. Rowling created?
- Were there any plot twists that surprised or impressed you?
- How did you feel about the way the series concluded?

Feel free to include any memorable moments, emotional responses, or personal reflections as well.
Let your imagination fly with your review, just like a broomstick in a Quidditch match!
"""
ELASTICSEARCH_URI = "http://localhost:9200"
ELASTICSEARCH_INDEX="default"


def elastic_search_knn(es_client, vector, field="query_vector"):
    search_query = {
        "knn": {
            "field": field,
            "query_vector": vector,
            "k": 5,
            "num_candidates": 10000,
        },
        "_source": [
            "title",
            "review_summary",   
            "review_text",
            "description",
            "authors",
            "publisher",
            "categories",
            "review_score",
            "document_id",
        ]
    }
    es_results = es_client.search(
        index=ELASTICSEARCH_INDEX,
        body=search_query
    )
    result_docs = []
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])
    return result_docs





class ElasticSearchTest(unittest.TestCase):

    def test_elasticsearch(self):

        model_name, __ = "all-mpnet-base-v2", 768
        model = SentenceTransformer(model_name)

        es_client = Elasticsearch(ELASTICSEARCH_URI) 
        vectorized_message = model.encode(RAG_PROMPT)

        documents = elastic_search_knn(es_client, vectorized_message, 'text_vector')
        print(len(documents))
        print(json.dumps(documents, indent=4, sort_keys=True))

if __name__ == '__main__':
    unittest.main()