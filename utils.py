import os
import string

from filetype import filetype


def valid_watermark(watermark_path):
    if not os.path.exists(watermark_path):
        print("Watermark doesn't exist")
        return False

    kind = filetype.guess(watermark_path)
    if kind is None:
        print('Cannot guess watermark file type')
        return False

    if not kind.mime.startswith('image'):
        print(f'Watermark file type is not image. Mime: [{kind.mime}]')
        return False

    return True


def valid_prefix(prefix):
    whitelist_chars = string.ascii_letters + string.digits + '_-.'

    if not len(prefix):
        print("Prefix must have at least one character")
        return False

    if not all(c in whitelist_chars for c in prefix):
        print(f"Prefix contains invalid characters. Allowed characters: [{whitelist_chars}]")
        return False

    return True
