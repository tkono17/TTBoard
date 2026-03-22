import typer
import logging
from ..tools import AppRunner
from ..app import App

log = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def runMacro(macro_file: str):
    log.info(f'Run macro from {macro_file}')
    tbapp = App()
    runner = AppRunner(tbapp)
    runner.run(macro_file)
    
def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-10s %(levelname)-6s %(message)s')
    app()

if __name__ == '__main__':
    main()
    
