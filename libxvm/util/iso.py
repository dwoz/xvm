'''
Utility methods for working with iso9660 filesystem images
'''
import os
import isoparser

def isiso(path):
    "True if the file looks like an iso"
    try:
        parsed = isoparser.parse(path)
    except isoparser.source.SourceError:
        return False
    return True


def iso_walk(path, root, top_down=False):
    dirs = []
    files = []
    for i in root.children:
        ipath = os.path.join(path, i.name)
        if i.is_directory:
            dirs.append((ipath, i))
        else:
            files.append((ipath, i))
    if top_down:
        for d in dirs:
            for b in iso_walk(*d, top_down=top_down):
                yield b
        yield (path, root), dirs, files
    else:
        yield (path, root), dirs, files
        for d in dirs:
            for b in iso_walk(*d):
                yield b


def extract_file(image, extract_file, to_file):
    extract_dir = os.path.dirname(extract_file)
    extract_filename = os.path.basename(extract_file)
    def matches(path):
        return os.path.dirname(path).decode() == extract_dir and \
        os.path.basename(path).decode() == extract_filename
    iso = isoparser.parse(image)
    for root, dirs, files in iso_walk(b'', iso.root):
        path, root = root
        for fpath, file in files:
            if matches(fpath):
                stream = file.get_stream()
                with open(to_file, 'wb') as fp:
                    while True:
                        chunk = stream.read(1024 * 1024)
                        if not chunk:
                            break
                        fp.write(chunk)
                return
    raise Exception("File not found")

