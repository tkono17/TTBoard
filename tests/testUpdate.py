import os
import sys
from typing import Optional, Any
import typer
import json
import jsonpath
import logging
from ..app import App

log = logging.getLogger(__name__)

app = typer.Typer()

def updateValue(objs, key, value):
    simple_list = False
    if len(objs) > 0:
        if type(obj) in (int, float, str): simple_list = True
    if simple_list:
        log.info(f'  Set all elements to {value}')
        for i in range(len(objs)):
            objs[i] = value
    else:
        for obj in objs:
            jsonpath
            if key in obj.keys():
                log.info(f'  Set obj[{key}] to {value}')
                obj[key] = value
    pass

def incrementList(objs):
    if len(objs)>0:
        log.info(f'  Append a copy of the last element to the list')
        objs.append(objs[-1])
    pass

@app.command()
def testUpdate(document_file: str, module_name: str,
               selector_name: Optional[str] = None,
               selector_args: list[str] | None = None,
               key: Optional[str] = None,
               value: Optional[str] = None,
               output_file_name: str | None = None):
    appControl = App()

    m = appControl.loadModule(module_name)
    selectors = m.getAllSelectors()
    log.info(f'{len(selectors)} JsonSelectors in module {module_name}')

    appControl.openJsonFile(document_file)

    if key is not None:
        try:
            ikey = int(key)
            key = ikey
        except ValueError:
            log.warning(f'  Key is not int')

    if value is not None:
        try:
            ivalue = int(value)
            value = ivalue
        except ValueError:
            log.warning(f'  Value is not int')
        
    if selector_name is None:
        for selector in selectors:
            log.info(f"  Test selector '{selector.name}'")
            args = [ '*' ] * selector.nArgs
            x = selector.findall(appControl.model.document, *args)
            log.info(f'    --> {len(x)} entries')
    else:
        selector = None
        x = None
        v = list(filter(lambda x: x.name == selector_name, selectors))
        if len(v) > 0:
            selector = v[0]
        if selector is not None:
            log.info(f"  Test selector '{selector.name}'")
            #x = selector.findall(appControl.model.document, *selector_args)
            jsonpath.patch.apply(operations, appControl.model.document)
        if output_file_name is not None:
            appControl.saveJsonFile(output_file_name)
    pass
    
def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-10s %(levelname)-5s %(message)s')
    app()

if __name__ == '__main__':
    main()
    
