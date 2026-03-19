import os
import sys
import typer
import typing
import json
import jsonpath
import logging
from ..app import App

log = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def testSelector(document_file: str, module_name: str,
                 selector_name: typing.Optional[str] = None,
                 selector_args: list[str] | None = None,
                 columns: list[str] | None = None):
    appControl = App()

    m = appControl.loadModule(module_name)
    selectors = m.getAllSelectors()
    log.info(f'{len(selectors)} JsonSelectors in module {module_name}')

    appControl.openJsonFile(document_file)

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
            x = selector.findall(appControl.model.document, *selector_args)
        if x is not None:
            if columns is not None:
                for ix, data in enumerate(x):
                    log.info(f'    Entry {ix}')
                    for cname in columns:
                        log.info(f'      {cname}: {data[cname]}')
            else:
                log.info(f'    --> {len(x)} entries')
    pass
    
def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-10s %(levelname)-5s %(message)s')
    app()

if __name__ == '__main__':
    main()
    
