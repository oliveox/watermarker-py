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


def get_valid_media_files(paths: List[str]) -> list[File]:
    try:
        valid_media_files: list[File] = []
        for path in paths:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file() and valid_media_file(entry.path):
                        valid_media_files.append(File(entry.path))
                    elif entry.is_dir():
                        get_valid_media_files([entry.path])
                    else:
                        logger.warning(
                            f"Path is not directory nor file. Skipping it. Path: {entry.path}"
                        )

        return valid_media_files
    except OSError as e:
        logger.info("Failed while validating paths")
        logger.exception(e)

        return []


def watermark_files(media_files: list[File]) -> None:
    for media_file in media_files:
        try:
            watermark_file(media_file)
        except Exception as e:
            logger.info(f"Failed to watermark file. Skipping: {media_file.path}")
            logger.exception(e)


def watermark_image(file: File) -> None:
    logger.info(f"Watermarking image: {file.path}")

    orientation = file.orientation

    overlay = config_manager.get_image_watermark_overlay(orientation)
    transpose = config_manager.get_image_transpose(orientation)

    watermark_file_path = config_manager.watermark_file_path
    if not watermark_file_path:
        raise ValueError("Watermark file path is not set")

    watermark_scaling = file.watermark_scaling
    output_file_path = file.output_file_path

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
    logger.info(f"Watermarking video: {file.path}")

    watermark_file_path = config_manager.watermark_file_path
    if not watermark_file_path:
        raise ValueError("Watermark file path is not set")

    overlay = config_manager.video_watermark_overlay
    transpose = config_manager.video_transpose

    watermark_scaling = file.watermark_scaling
    output_file_path = file.output_file_path

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

    with open("logs.log", "a") as log_file:
        if verbosity:
            logger.debug("\n\n############ FFmpeg logs START ############\n\n")
            # logs on all handlers
            for line in proc.stdout:
                logger.debug(line.decode("utf-8").replace("\n", ""))
        else:
            log_file.write("\n\n############ FFmpeg logs START ############\n\n")
            # by default log file contains all logs hence log only in the file
            for line in proc.stdout:
                log_file.write(line.decode("utf-8"))

        if verbosity:
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
