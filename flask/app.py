import os
import logging

from dotenv import load_dotenv

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from flask import Flask, request, jsonify
from openai import OpenAI


logging.basicConfig(filename='log_file_name.log',
    level=logging.INFO, 
    format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
)


if os.path.isfile('.env'):
    load_dotenv()


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# model_name, __ = 'multi-qa-MiniLM-L6-cos-v1', 384
model_name, __ = "all-mpnet-base-v2", 768
model = SentenceTransformer(model_name)
model.encode("hello world").tolist()

OLLAMA_URI = os.getenv('OLLAMA_URI', 'http://localhost:11434/v1/')
OLLAMA_KEY = os.getenv('OLLAMA_KEY', 'ollama')
ollama_client = OpenAI(
    base_url=OLLAMA_URI,
    api_key=OLLAMA_KEY,
)

ELASTICSEARCH_URI = os.getenv('ELASTICSEARCH_URI', 'http://localhost:9200')
ELASTICSEARCH_INDEX = os.getenv('ELASTICSEARCH_INDEX', 'default-index-name')
es_client = Elasticsearch(ELASTICSEARCH_URI) 

PROMPT_HEADER = ("As a highly knowledgeable Book Review Assistant, your task is to recommend books, " 
    "provide thoughtful reviews, and offer personalized suggestions. " 
    "With a deep understanding of various genres, you will assess books based on criteria " 
    "such as writing style, plot, character development, themes, and reader preferences. ")


def elastic_search_knn(vector, field="query_vector"):
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


def generate_context(documents):
    context = "" 
    for doc in documents:
        text = ""
        for key, value in doc.items():
            text = text + f"{key}: {value}\n"
        context = context + f"{text}\n"
    return context


def generate_prompt(context, message, prompt_header=PROMPT_HEADER):
    return f"{context}\n{prompt_header}\n{message}"


def llm(client, prompt, model='gemma:2b'):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


app = Flask(__name__)


@app.route('/')
def index():
    return 'Welcome'


@app.route('/api/ollamarag', methods=['post'])
def api_rag():
    logging.info("Getting message...")
    if request.is_json:
        data = request.get_json()
        if 'message' in data:
            message = data['message']
            vectorized_message = model.encode(message).tolist()
            documents = elastic_search_knn(vectorized_message, 'text_vector')
            doc_context = generate_context(documents)
            llm_prompt = generate_prompt(context=doc_context, prompt_header=PROMPT_HEADER, message=message)
            out_llm = llm(client=ollama_client, prompt=llm_prompt, model='gemma:2b')
            print(out_llm)
            response = {
                'status': 'success',
                'message': out_llm,
                'documents': documents,
                'prompt_header': PROMPT_HEADER
            }
            return jsonify(response), 200
        return jsonify({'error': 'message key not found in JSON payload'}), 400
    return jsonify({'error': 'Request must be JSON formatted'}), 400


@app.route('/api/openairag', methods=['post'])
def api_openairag():
    logging.info("Getting message...")
    if request.is_json:
        data = request.get_json()
        if 'message' in data:
            message = data['message']
            vectorized_message = model.encode(message).tolist()
            documents = elastic_search_knn(vectorized_message, 'text_vector')
            doc_context = generate_context(documents)
            llm_prompt = generate_prompt(context=doc_context, prompt_header=PROMPT_HEADER, message=message)
            out_llm = llm(client=ollama_client, prompt=llm_prompt, model='gemma:2b')
            print(out_llm)
            response = {
                'status': 'success',
                'message': out_llm,
                'documents': documents,
                'prompt_header': PROMPT_HEADER
            }
            return jsonify(response), 200
        return jsonify({'error': 'message key not found in JSON payload'}), 400
    return jsonify({'error': 'Request must be JSON formatted'}), 400


@app.route('/api/ollama', methods=['post'])
def api_ollama():
    if request.is_json:
        data = request.get_json()
        if 'message' in data:
            message = data['message']
            response = {
                'status': 'success',
                'message': llm(client=openai_client, model=OPENAI_MODEL, prompt=message)
            }
            return jsonify(response), 200
        return jsonify({'error': 'message key not found in JSON payload'}), 400
    return jsonify({'error': 'Request must be JSON formatted'}), 400


@app.route('/api/openai', methods=['post'])
def api_openai():
    if request.is_json:
        data = request.get_json()
        if 'message' in data:
            message = data['message']
            response = {
                'status': 'success',
                'message': llm(client=openai_client, model=OPENAI_MODEL, prompt=message)
            }
            return jsonify(response), 200
        return jsonify({'error': 'message key not found in JSON payload'}), 400
    return jsonify({'error': 'Request must be JSON formatted'}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
    # app.run()
