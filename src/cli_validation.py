import os
import string

from filetype import filetype


def valid_input_paths(paths: list[str]) -> bool:
    if not len(paths):
        print("No input paths specified")
        return False

    if not all(os.path.exists(i) for i in paths):
        print("Input contains a path that doesn't exist")
        return False

    return True


def valid_watermark_file(file_path: str) -> bool:
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


def valid_prefix(prefix: str) -> bool:
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


def valid_output_path(file_path: str) -> bool:
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        print("Specified output path already exists and is not a directory")
        return False

    if not os.path.exists(file_path):
        print("Output directory path doesn't exist. Creating it.")

        try:
            os.makedirs(file_path)
        except Exception as e:
            print(f"Failed to create output directory. Error: {e}")
            return False

    return True
