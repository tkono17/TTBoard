import logging
import typer
from ..app import App
from ..view import ViewControl

log = logging.getLogger(__name__)
app = typer.Typer()

def startGui():
    log.info(f'Start TTBoard application in GUI mode')
    pass

def runBatch():
    log.info(f'Start TTBoard application in batch mode')
    app = App()
    fn1 = '../../tkono-site/source/files/memberList.json'
    fn2 = './memberList0.json'
    app.openJsonFile(fn1)
    app.saveJsonFile(fn2)
    pass

@app.command('run')
def run(no_gui: bool = False):
    if (no_gui):
        runBatch()
    else:
        startGui()
    pass

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-20s %(levelname)-8s %(message)s')
    app()
    
if __name__ == '__main__':
    main()
    
