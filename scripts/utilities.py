import mimetypes
import importlib

encoding_to_module = {
    'gzip': 'gzip',
    # 'bzip2': 'bz2', # Enable in Python 3
    # 'xz': 'lzma', # Enable in Python 3
}

def get_opener(filename):
    """
    Automatically detect compression and return the file opening function.
    """
    type_, encoding = mimetypes.guess_type(filename)
    if encoding is None:
        opener = open
    else:
        module = encoding_to_module[encoding]
        opener = importlib.import_module(module).open
    return opener
