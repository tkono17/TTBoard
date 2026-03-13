import io
import importlib.resources
from PIL import Image, ImageTk
import logging

log = logging.getLogger(__name__)

def openAssetImage(fileName):
    image = None
    shape = (15, 15)
    with importlib.resources.open_binary('ttboard.assets', fileName) as fin:
        image_bytes = fin.read()
        image = Image.open(io.BytesIO(image_bytes))
        image1 = image.resize(shape, Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image1)
    return image

