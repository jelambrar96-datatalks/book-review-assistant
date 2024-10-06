import unittest
from app import app  # Assuming your Flask app is saved in a file named app.py

class FlaskMessageAPITestCase(unittest.TestCase):
    
    def setUp(self):
        # Set up the test client for the Flask app
        self.app = app.test_client()
        self.app.testing = True  # Enable testing mode

    def test_valid_message_post(self):
        # Simulate a valid POST request with a 'message' key
        response = self.app.post('/message', 
                                 json={'message': 'Hello, Test!'})
        
        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response and check if 'message_received' is correct
        data = response.get_json()
        self.assertEqual(data['message_received'], 'Hello, Test!')
        self.assertEqual(data['status'], 'success')

    def test_missing_message_key(self):
        # Simulate a POST request without the 'message' key
        response = self.app.post('/message', 
                                 json={'other_key': 'No message'})
        
        # Check if the response status code is 400
        self.assertEqual(response.status_code, 400)
        
        # Parse the JSON response and check for the correct error message
        data = response.get_json()
        self.assertEqual(data['error'], 'message key not found in JSON payload')

    def test_non_json_request(self):
        # Simulate a POST request that is not JSON formatted
        response = self.app.post('/message', 
                                 data="This is not JSON",
                                 content_type='text/plain')
        
        # Check if the response status code is 400
        self.assertEqual(response.status_code, 400)
        
        # Parse the JSON response and check for the correct error message
        data = response.get_json()
        self.assertEqual(data['error'], 'Request must be JSON formatted')

if __name__ == '__main__':
    unittest.main()
