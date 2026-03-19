#!/usr/bin/env python3
import json
import jsonpath
import pytest
from pathlib import Path
import ttboard

inputJsonFile = Path(__file__).parent/'data/testInput.json'

@pytest.fixture(scope='module', autouse=True)
def app():
    appc = ttboard.App()
    appc.openJsonFile(inputJsonFile)
    return appc

def test_selector_ready(app):
    assert type(app.model.document) == dict

def test_selector_int(app):
    expr = '$.data1'
    x = app.findall(expr)
    assert len(x) == 1 and x[0] == 1203

def test_selector_float(app):
    expr = '$.pi'
    x = app.findall(expr)
    assert len(x) == 1 and x[0] == 3.14159265

def test_selector_str(app):
    expr = '$.message'
    x = app.findall(expr)
    assert len(x) == 1 and x[0] == 'Hello, JSON!'

def test_selector_list(app):
    expr = '$.numbers'
    x = app.findall(expr)
    assert len(x) == 1 and x[0] == list(range(10))

def test_selector_objects(app):
    x = app.getList('objects', '*')
    assert len(x) == 3

def test_selector_field(app):
    expr = '$.objects[?@.name == "B"].dates[*]'
    x = jsonpath.findall(expr, app.model.document)
    assert len(x) == 2 and x[0]['year'] == 1992
