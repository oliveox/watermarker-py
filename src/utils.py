import logging
import os
import subprocess
from typing import List, Union

from filetype import filetype

from logger import verbosity
from src.cli_configuration import cli_configuration
from src.config import IncorrectWatermarkConfigurationError, config_manager
from src.custom_types import FileType
from src.ffmpeg_utils_mixin import FFmpegUtilsMixin
from src.file import File

logger = logging.getLogger("watermarker")


def get_valid_media_files(paths: List[str], root_node: str = None, root_iteration: bool = False) -> list[File]:
    valid_media_files: list[File] = []
    try:
        for path in paths:
            if os.path.isfile(path):
                valid_media_files.append(File(path=path, output_subdir=""))
            elif os.path.isdir(path):
                # os.scandir is faster than os.listdir
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file() and valid_media_file(entry.path):
                            output_subdir = (
                                get_output_subdir(entry.path, path, root_node)
                                if cli_configuration.keep_output_tree
                                else ""
                            )
                            valid_media_files.append(File(path=entry.path, output_subdir=output_subdir))
                        elif entry.is_dir():
                            valid_media_files.extend(
                                get_valid_media_files(
                                    paths=[entry.path],
                                    root_node=path if root_iteration else root_node,
                                )
                            )
                        else:
                            logger.warning(f"Path is not directory nor file. Skipping it. Path: {entry.path}")
            else:
                logger.warning(f"Path is not directory nor file. Skipping it. Path: {entry.path}")
    except OSError as e:
        logger.info("Failed while validating paths")
        logger.exception(e)

    return valid_media_files


def get_output_subdir(file_path, reference_path, root_node):
    subdir = os.path.dirname(file_path.replace(root_node or reference_path, ""))

    # os.path.join doesn't work here
    return os.path.basename(root_node or reference_path) + subdir


def watermark_files(media_files: list[File]) -> None:
    for media_file in media_files:
        try:
            logger.info(f"\nWatermarking {media_file.path}")
            logger.debug(media_file)

            if not cli_configuration.overwrite and os.path.exists(media_file.output_file_path):
                logger.info("Output file already exists. Skipping ... ")
                continue
            watermark_file(media_file)
        except IncorrectWatermarkConfigurationError as e:
            raise e  # incorrect watermark configurations should stop the whole watermarking process
        except Exception as e:
            logger.info("File watermarking process failed. Skipping ...")
            logger.exception(e)


def run_command(command: Union[str, list]) -> None:
    # log command both as list and string (easy copy-paste)
    logger.debug(f"Running command: \n{command} \n{' '.join(command)}")

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    display_commands_output = verbosity == 2

    with open("logs.log", "a") as log_file:
        if display_commands_output:
            logger.debug("\n\n############ FFmpeg logs START ############\n\n")
            # log using on all handlers
            for line in proc.stdout:
                logger.debug(line.decode("utf-8").replace("\n", ""))
        else:
            log_file.write("\n\n############ FFmpeg logs START ############\n\n")
            # by default log file contains all logs (debug) hence logging only to file
            for line in proc.stdout:
                log_file.write(line.decode("utf-8"))

        if display_commands_output:
            logger.debug("\n\n############ FFmpeg logs END ############\n\n")
        else:
            log_file.write("\n\n############ FFmpeg logs END ############\n\n")

    proc.wait()


def watermark_file(file: File) -> None:
    if file.type not in [FileType.IMAGE, FileType.VIDEO]:
        raise ValueError(f"Invalid file type: {file.type}. Watermarking is supported only for images and videos. ")

    overlay = config_manager.watermark_overlay(
        file_path=file.path, width=file.dimensions["width"], height=file.dimensions["height"]
    )
    watermark_file_path = cli_configuration.watermark_file_path
    watermark_scaling = file.watermark_scaling
    output_file_path = file.output_file_path

    if cli_configuration.keep_output_tree:
        # create output directory tree if it doesn't exist
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    apply_watermark_command = FFmpegUtilsMixin.get_watermarking_command(
        input_file_path=file.path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        watermark_scaling=watermark_scaling,
    )

    run_command(apply_watermark_command)


def valid_media_file(path: str) -> bool:
    kind = filetype.guess(path)
    if kind is None:
        logger.debug(f"Cannot find file type for: {path}")
        return False

    if not kind.mime.startswith("image") and not kind.mime.startswith("video"):
        logger.debug(f"Invalid media file: [{path}]. Mime: [{kind.mime}]")
        return False

    return True
