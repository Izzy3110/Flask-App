import unittest
import json

from flask import request, jsonify

import inspect
import os
import sys

import importlib.util
import sys


def lazy_import(name):
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
src_dir = os.path.join(test_dir, '..', 'flask_app')
sys.path.append(src_dir)
src_dir = os.path.join(test_dir, '..', 'flask_app', 'wyl')
sys.path.append(src_dir)

print(sys.path)

print(test_dir)
if os.path.isfile(os.path.join(test_dir, "..", "flask_app", "wyl", "__init__.py")):
    wsgi = lazy_import("wsgi")
    app = wsgi.create_app()








