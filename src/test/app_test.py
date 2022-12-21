import os
import sys
import importlib
import inspect
import unittest
import json
from flask import request, jsonify
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
sys.path.append(test_dir)

flask_app_dir = os.path.join(test_dir, '..', 'flask_app')
sys.path.append(flask_app_dir)


wyl_dir = os.path.join(test_dir, '..', 'flask_app', 'wyl')
sys.path.append(wyl_dir)


wsgi = lazy_import("wsgi")
wyl = lazy_import("wyl")

tested_app = wsgi.create_app()
if tested_app is not None:
    tested_app.secret_key = os.urandom(32)
    print(tested_app)
    print(type(tested_app))

if __name__ == '__main__':
    unittest.main()
