import filetype


def what(file, h=None):
    """Определяет тип изображения, эмулируя функциональность imghdr.what()"""
    if h is None and hasattr(file, "read"):
        h = file.read()
        file.seek(0)

    if h:
        kind = filetype.guess(h)
        if kind and kind.mime.startswith("image/"):
            return kind.extension

    return None
