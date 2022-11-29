import logging
import os
import shlex
import subprocess

from filetype import filetype

from src.config import config_manager
from src.ffmpeg_utils_mixin import FFmpegUtilsMixin
from src.file import File
from src.types import FileType


def get_valid_media_files(paths: list[str]) -> list[File]:
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
                        logging.warning(
                            f"Path nor directory nor file. Skipping it. Path: {entry.path}"
                        )

        return valid_media_files
    except OSError as e:
        logging.info("Failed while validating paths")
        logging.exception(e)


def watermark_files(media_files: list[File]) -> None:
    for media_file in media_files:
        try:
            watermark_file(media_file)
        except Exception as e:
            logging.info(f"Failed to watermark file. Skipping: {media_file.path}")
            logging.exception(e)


def watermark_image(file: File) -> None:
    logging.info(f"Watermarking image: {file.path}")

    orientation = file.orientation

    overlay = config_manager.get_image_watermark_overlay(orientation)
    transpose = config_manager.get_image_transpose(orientation)
    watermark_file_path = config_manager.watermark_file_path

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
    subprocess.run(
        shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )


def watermark_video(file: File) -> None:
    logging.info(f"Watermarking video: {file.path}")

    watermark_file_path = config_manager.watermark_file_path
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
    subprocess.run(
        shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )


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
        logging.debug(f"Cannot find file type for: {path}")
        return False

    if not kind.mime.startswith("image") and not kind.mime.startswith("video"):
        logging.debug(f"Invalid media file: [{path}]. Mime: [{kind.mime}]")
        return False

    return True
