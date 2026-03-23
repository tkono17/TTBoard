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

def readScalar(word: int | float | str):
    value = None
    try:
        value = int(word)
    except ValueError as e:
        pass
    if value is None:
        try:
            value = float(word)
        except ValueError as e:
            pass
    if value is None:
        value = word
    return value

def readKeyValue(kv_word):
    key, value = None, None
    words = kv_word.split(':')
    if len(words)==2:
        key, value = words
    elif len(words)==1:
        key = words[0]
        value = None
    else:
        log.warning(f'Key:Value from word {kv_word} cannot be decoded')
    return (key, value)
