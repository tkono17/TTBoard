import re
import logging

log = logging.getLogger(__name__)

def mainType(dataField):
    dtype = None
    stype = str(dataField.type)
    if stype.startswith('list'):
        dtype = list
    elif stype.find('typing.Optional')>=0:
        mg = re.search(r'typing.Optional[(.*?)]', stype)
        if mg:
            stype2 = mg.group(1)
            dtype = stype2
    else:
        dtype = str
    if dtype is None:
        log.warning(f'Cannot find the main type of {dataField}, use str')
        dtype = str
    return dtype

