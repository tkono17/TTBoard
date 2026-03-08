import os
import sys
import typer
import json
import jsonpath
import logging
from ..tools import JsonSelector

log = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def checkList(document_file: str, json_path: str):
    document = None
    log.info(f'Test JSONPath expression {json_path} in {document_file}')
    if os.path.exists(document_file):
        with open(document_file, 'r') as fin:
            document = json.load(fin)
    else:
        log.error(f'  JSON file {document_file} does not exist')
        sys.exit(-1)
    if document is None:
        log.error(f'  Failed to read JSON document from {document_file}')
        sys.exit(-1)

    data = jsonpath.findall(json_path, document)
    log.info(f'Found {len(data)} match(es)')
    
def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-20s %(levelname)-8s %(message)s')
    app()

if __name__ == '__main__':
    main()
    
