import typer
import logging
from ..tools import AppRunner
from ..app import App

log = logging.getLogger(__name__)

app = typer.Typer()

@app.command('macro')
def runMacro(macro_file: str):
    log.info(f'Run macro from {macro_file}')
    tbapp = App()
    runner = AppRunner(tbapp)
    runner.run(macro_file)
    
@app.command('show')
def showAllCommands():
    log.info(f'All commands:')
    tbapp = App()
    runner = AppRunner(tbapp)
    fnames = runner.allCommands()
    for fn in fnames:
        log.info(f'  {fn}')
        
def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-10s %(levelname)-6s %(message)s')
    app()

if __name__ == '__main__':
    main()
    
