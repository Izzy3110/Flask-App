import importlib
import inspect
import unittest
import json
from flask import request, jsonify
import os
import sys
from importlib import util


def lazy_import(name):
    spec = util.find_spec(name)
    loader = util.LazyLoader(spec.loader)
    spec.loader = loader
    module = util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module

test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
src_dir = os.path.join(test_dir, '..', 'flask_app')
sys.path.append(src_dir)
src_dir = os.path.join(test_dir, '..', 'flask_app', 'wyl')
sys.path.append(src_dir)


wsgi = lazy_import("wsgi")
wyl = lazy_import("wyl")

tested_app = wsgi.create_app()
tested_app.secret_key = os.urandom(32)


@tested_app.route('/api', methods=['GET', 'POST'])
def api():
    """
    /api entpoint
    GET - returns json= {'status': 'test'}
    POST -  {
            name - str not null
            age - int optional
            }
    :return:
    """
    if request.method == 'GET':
        return jsonify({'status': 'test'})
    elif request.method == 'POST':
        if wyl.validate_post_data(request.json):
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'bad input'}), 400


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
