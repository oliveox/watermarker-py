import os
import string
from typing import List

from filetype import filetype

from logger import logger


def valid_input_paths(paths: List[str]) -> bool:
    if not len(paths):
        logger.info("No input paths specified")
        return False

    if not all(os.path.exists(i) for i in paths):
        logger.info("Input contains a path that doesn't exist")
        return False

    return True


def valid_watermark_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        logger.info("Watermark file path doesn't exist")
        return False

    if not os.path.isfile(file_path):
        logger.info("Watermark path is not a file")
        return False

    kind = filetype.guess(file_path)
    if kind is None:
        logger.info("Cannot determine watermark file type")
        return False

    if not kind.mime.startswith("image"):
        logger.info("Watermark file type is not image")
        logger.debug(f"Mime: [{kind.mime}]")
        return False

    return True


def valid_prefix(prefix: str) -> bool:
    whitelist_chars = string.ascii_letters + string.digits + "_-."

    if not len(prefix):
        logger.info("Prefix must have at least one character")
        return False

    if not all(c in whitelist_chars for c in prefix):
        logger.info(
            f"Prefix contains invalid characters. Allowed characters: [{whitelist_chars}]"
        )
        return False

    return True


def valid_output_path(file_path: str) -> bool:
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        logger.info(
            "Specified output path already exists and is not a directory. Output path must be a directory or not exist"
        )
        return False

    if not os.path.exists(file_path):
        logger.info("Output directory path doesn't exist. Creating it.")

        try:
            os.makedirs(file_path)
        except Exception as e:
            logger.info("Failed to create output directory")
            logger.exception(e)
            return False

    return True
