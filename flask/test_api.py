import unittest
import json
import requests


class FLaskOllamaAPI(unittest.TestCase):

    def test_api_ollama_route(self):

        url = "http://localhost:5000/api/ollama"

        data = {
            "message": "what is 5 * 5?"
        }

        res = requests.post(url=url, json=data, timeout=30)
        print(res.status_code)

        

        res_json = res.json()

        print(json.dumps(res_json, indent=4))

if __name__ == '__main__':
    unittest.main()