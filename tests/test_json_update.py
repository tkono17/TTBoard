#!/usr/bin/env python3
import os
import json
import jsonpath
import pytest
from pathlib import Path
import ttboard

inputJsonFile = Path(__file__).parent/'data/testInput.json'
outputJsonFile = 'out.json'

def read_json_file(fn):
    data = None
    with open(fn, 'r') as f:
        data = json.load(f)
    return data

@pytest.fixture(scope='module', autouse=True)
def app():
    appc = ttboard.App()
    appc.openJsonFile(inputJsonFile)
    return appc

def test_update_scalar(app, capsys):
    jpath = '$.pi'
    x = jsonpath.match(jpath, app.model.document)
    x2 = 2.0*x.obj
    x.parent.obj['pi'] = x2
    app.saveJsonFile(outputJsonFile)

    epath = x.path
    doc2 = read_json_file(outputJsonFile)
    y = jsonpath.findall(epath, doc2)
    assert y[0] == x2

def test_update_list(app):
    pass

def test_update_object(app):
    pass

def test_update_objects(app):
    pass

def test_update_field(app):
    newName = 'Andy'
    i = 0
    v = app.getList('objects', (str(i)))
    m = app.listMatchedPaths[i]
    m.pointer().resolve(app.model.document)['name'] = newName
    app.saveJsonFile(outputJsonFile)

    doc2 = read_json_file(outputJsonFile)
    pointer = m.pointer().join('name')
    y = pointer.resolve(doc2)
    assert y == newName

