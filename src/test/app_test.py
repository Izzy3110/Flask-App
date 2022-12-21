import importlib
import inspect
import unittest
import json
from flask import request, jsonify
import os
import sys
from importlib import util

def sample_url():
    """Target URL to scrape metadata."""
    return 'https://hackersandslackers.com/creating-django-views/'

def expected_json():
    """Expected metadata to be returned."""
    return {
        "@context": "https://schema.org/",
        "@type": "Article",
        "author": {
            "@type": "Person",
            "name": "Todd Birchard",
            "image": "https://cdn.hackersandslackers.com/2021/09/avimoji.jpg",
            "sameAs": "[\"https://toddbirchard.com\", \"https://twitter.com/toddrbirchard\", \"https://www.facebook.com/https://github.com/toddbirchard\"]"
        },
        "keywords": "Django, Python, Software",
        "headline": "Creating Interactive Views in Django",
        "url": "https://hackersandslackers.com/creating-django-views/",
        "datePublished": "2020-04-23T12:21:00.000-04:00",
        "dateModified": "2020-12-25T00:51:36.000-05:00",
        "image": {
            "@type": "ImageObject",
            "url": "https://cdn.hackersandslackers.com/2020/11/django-views.jpg",
            "width": 1000,
            "height": 523
        },
        "publisher": {
            "@type": "Organization",
            "name": "Hackers and Slackers",
            "logo": {
                "@type": "ImageObject",
                "url": "https://cdn.hackersandslackers.com/logo/logo.png",
                "width": 60,
                "height": 60
            }
        },
        "description": "Create interactive user experiences by writing Django views to handle dynamic content, submitting forms, and interacting with data.",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": "https://hackersandslackers.com"
        }
    }



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
if tested_app is not None:
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
            self.assertEqual(r.status_code, 200)
            
            
        def test_get_login_endpoint(self):
            r = self.app.get('/login')
            self.assertEqual(r.status_code, 200)
        
            # self.assertEqual(r.data, b'Hello World!')
        '''
        def test_post_hello_endpoint(self):
            r = self.app.post('/')
            self.assertEqual(r.status_code, 405)

        def test_endpoints_scrape_exists(self):
            r = self.app.get('/scrape/')
            self.assertEqual(r.status_code, 302)
            
            
        
        
        LOGIN REQUIRED
        
        def test_post_scrape_url(self):
            global expected_json
            
            url = sample_url()
            """Match scrape's fetched metadata to known value."""
            # metadata = scrape(url)
            # assert metadata == expected_json
            r = self.app.post('/scrape/',
                              content_type='application/json',
                              data=json.dumps({'url': url}))
            # self.assertEqual(r.json, {'status': 'OK'})
            self.assertEqual(r.status_code, 302)
        


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
        '''

if __name__ == '__main__':
    unittest.main()
