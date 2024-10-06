import unittest

import requests


SIMPLE_OLLAMA_PROMPT = "what is 5 * 5?"
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



class FlasAPITest(unittest.TestCase):
    
    def test_request_ollama(self):
        url = "http://localhost:5000/api/ollama"
        data = {
            "message": SIMPLE_OLLAMA_PROMPT
        }
        res = requests.post(url=url, json=data, timeout=30)
        if res.status_code != 200:
            raise ValueError(f"Invalid status code {res.status_code}")
        res_json = res.json()
        llm_output = res_json["message"]
        print(llm_output)


    def test_request_openai(self):
        url = "http://localhost:5000/api/openai"
        data = {
            "message": SIMPLE_OLLAMA_PROMPT
        }
        res = requests.post(url=url, json=data, timeout=30)
        if res.status_code != 200:
            raise ValueError(f"Invalid status code {res.status_code}")
        res_json = res.json()
        llm_output = res_json["message"]
        print(llm_output)


    def test_request_ollamarag(self):
        url = "http://localhost:5000/api/ollamarag"
        data = {
            "message": RAG_PROMPT
        }
        res = requests.post(url=url, json=data, timeout=500)
        if res.status_code != 200:
            raise ValueError(f"Invalid status code {res.status_code}")
        res_json = res.json()
        llm_output = res_json["message"]
        print(llm_output)


    def test_request_openairag(self):
        url = "http://localhost:5000/api/openairag"
        data = {
            "message": RAG_PROMPT
        }
        res = requests.post(url=url, json=data, timeout=500)
        if res.status_code != 200:
            raise ValueError(f"Invalid status code {res.status_code}")
        res_json = res.json()
        llm_output = res_json["message"]
        print(llm_output)



if __name__ == '__main__':
    unittest.main()
