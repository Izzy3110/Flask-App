import unittest
from src import app as tested_app
import json


class FlaskAppTests(unittest.TestCase):

    def setUp(self):

        tested_app.config['TESTING'] = True
        self.app = tested_app.test_client()

    def test_get_hello_endpoint(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 302)
        # self.assertEqual(r.data, b'Hello World!')

    def test_post_hello_endpoint(self):
        r = self.app.post('/')
        self.assertEqual(r.status_code, 405)

    def test_endpoints_scrape_exists(self):
        r = self.app.get('/scrape/')
        self.assertEqual(r.status_code, 200)

    def test_endpoints_api_get(self):
        r = self.app.get('/api')
        self.assertEqual(r.json, {'status': 'test'})

    def test_endpoints_api_post_correct(self):
        r = self.app.post('/api',
                          content_type='application/json',
                          data=json.dumps({'name': 'Den', 'age': 100}))
        self.assertEqual(r.json, {'status': 'OK'})
        self.assertEqual(r.status_code, 200)

        r = self.app.post('/api',
                          content_type='application/json',
                          data=json.dumps({'name': 'Den'}))
        self.assertEqual(r.json, {'status': 'OK'})
        self.assertEqual(r.status_code, 200)

    def test_endpoints_api_post_not_dict(self):
        r = self.app.post('/api',
                          content_type='application/json',
                          data=json.dumps([{'name': 'Den'}]))
        self.assertEqual(r.json, {'status': 'bad input'})
        self.assertEqual(r.status_code, 400)

    def test_endpoints_api_post_no_name(self):
        r = self.app.post('/api',
                          content_type='application/json',
                          data=json.dumps({'age': 100}))
        self.assertEqual(r.json, {'status': 'bad input'})
        self.assertEqual(r.status_code, 400)

    def test_endpoints_api_post_bad_age(self):
        r = self.app.post('/api',
                          content_type='application/json',
                          data=json.dumps({'name': 'Den', 'age': '100'}))
        self.assertEqual(r.json, {'status': 'bad input'})
        self.assertEqual(r.status_code, 400)


if __name__ == '__main__':
    unittest.main()
