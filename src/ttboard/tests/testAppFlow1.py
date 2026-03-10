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
def testAppFlow1(document_file: str,
                 selector_name: typing.Optional[str] = None,
                 selector_args: list[str] | None = None,
                 columns: list[str] | None = None):
    appControl = App()

    appControl.openJsonFile(document_file)
    selectors = None
    if appControl.dataModule is not None:
        selectors = appControl.dataModule.getAllSelectors()
    
    if selector_name is None:
        for selector in selectors:
            log.info(f"  Test selector '{selector.name}'")
            args = [ '*' ] * selector.nArgs
            log.info(f'  args = {args}')
            x = appControl.getList(selector.name, *args)
            if x is not None:
                log.info(f'    --> {len(x)} entries')
            else:
                log.info(f'    --> None')
    else:
        log.info(f"  Test selector '{selector.name}'")
        x = appControl.getList(selector_name, *selector_args)
        if x is not None and columns is not None:
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
    
