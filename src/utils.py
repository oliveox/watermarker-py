import os
import shlex
import subprocess
from typing import List, Union

from filetype import filetype

from logger import logger, verbosity
from src.config import config_manager
from src.custom_types import FileType
from src.ffmpeg_utils_mixin import FFmpegUtilsMixin
from src.file import File


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
                                if config_manager.keep_output_tree
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
            watermark_file(media_file)
        except Exception as e:
            logger.info(f"Watermarking process failed. Skipping ...")
            logger.exception(e)


def watermark_image(file: File) -> None:
    orientation = file.orientation

    overlay = config_manager.get_image_watermark_overlay(orientation)
    transpose = config_manager.get_image_transpose(orientation)

    watermark_file_path = config_manager.watermark_file_path
    if not watermark_file_path:
        raise ValueError("Watermark file path is not set")

    watermark_scaling = file.watermark_scaling
    output_file_path = file.output_file_path

    if config_manager.keep_output_tree:
        # create output directory tree if it doesn't exist
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    command = FFmpegUtilsMixin.get_watermarking_command(
        input_file_path=file.path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        transpose=transpose,
        watermark_scaling=watermark_scaling,
    )

    run_command(shlex.split(command))


def watermark_video(file: File) -> None:
    watermark_file_path = config_manager.watermark_file_path
    if not watermark_file_path:
        raise ValueError("Watermark file path is not set")

    overlay = config_manager.video_watermark_overlay
    transpose = config_manager.video_transpose

    watermark_scaling = file.watermark_scaling
    output_file_path = file.output_file_path

    if config_manager.keep_output_tree:
        # create output directory tree if it doesn't exist
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    command = FFmpegUtilsMixin.get_watermarking_command(
        input_file_path=file.path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        transpose=transpose,
        watermark_scaling=watermark_scaling,
    )

    run_command(shlex.split(command))


def run_command(command: Union[str, list]) -> None:
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
    if file.type == FileType.IMAGE:
        watermark_image(file)
    elif file.type == FileType.VIDEO:
        watermark_video(file)
    else:
        raise Exception(f"Invalid file type: {file.type}")


def valid_media_file(path: str) -> bool:
    kind = filetype.guess(path)
    if kind is None:
        logger.debug(f"Cannot find file type for: {path}")
        return False

    if not kind.mime.startswith("image") and not kind.mime.startswith("video"):
        logger.debug(f"Invalid media file: [{path}]. Mime: [{kind.mime}]")
        return False

    return True
