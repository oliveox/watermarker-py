import logging
import os
import string

from filetype import filetype


def valid_input_paths(paths: list[str]) -> bool:
    if not len(paths):
        logging.info("No input paths specified")
        return False

    if not all(os.path.exists(i) for i in paths):
        logging.info("Input contains a path that doesn't exist")
        return False

    return True


def valid_watermark_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        logging.info("Watermark file path doesn't exist")
        return False

    kind = filetype.guess(file_path)
    if kind is None:
        logging.info("Cannot determine watermark file type")
        return False

    if not kind.mime.startswith("image"):
        logging.info("Watermark file type is not image")
        logging.debug(f"Mime: [{kind.mime}]")
        return False

    return True


def valid_prefix(prefix: str) -> bool:
    whitelist_chars = string.ascii_letters + string.digits + "_-."

    if not len(prefix):
        logging.info("Prefix must have at least one character")
        return False

    if not all(c in whitelist_chars for c in prefix):
        logging.info(
            f"Prefix contains invalid characters. Allowed characters: [{whitelist_chars}]"
        )
        return False

    return True


def valid_output_path(file_path: str) -> bool:
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        logging.info(
            "Specified output path already exists and is not a directory. Output path must be a directory or not exist"
        )
        return False

    if not os.path.exists(file_path):
        logging.info("Output directory path doesn't exist. Creating it.")

        try:
            os.makedirs(file_path)
        except Exception as e:
            logging.info("Failed to create output directory")
            logging.exception(e)
            return False

    return True
