import os
import string

from filetype import filetype


def valid_input_paths(paths):
    if not len(paths):
        print("No input paths specified")
        return False

    if not all(os.path.exists(i) for i in paths):
        print("Input contains a path that doesn't exist")
        return False

    return True


def valid_watermark_file(file_path):
    if not os.path.exists(file_path):
        print("Watermark doesn't exist")
        return False

    kind = filetype.guess(file_path)
    if kind is None:
        print("Cannot guess watermark file type")
        return False

    if not kind.mime.startswith("image"):
        print(f"Watermark file type is not image. Mime: [{kind.mime}]")
        return False

    return True


def valid_prefix(prefix):
    whitelist_chars = string.ascii_letters + string.digits + "_-."

    if not len(prefix):
        print("Prefix must have at least one character")
        return False

    if not all(c in whitelist_chars for c in prefix):
        print(
            f"Prefix contains invalid characters. Allowed characters: [{whitelist_chars}]"
        )
        return False

    return True


def valid_output_path(path):
    if os.path.exists(path) and not os.path.isdir(path):
        print("Specified output path already exists and is not a directory")
        return False

    if not os.path.exists(path):
        print("Output directory path doesn't exist. Creating it.")

        try:
            os.makedirs(path)
        except Exception as e:
            print(f"Failed to create output directory. Error: {e}")
            return False

    return True
