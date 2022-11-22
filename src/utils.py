import os
import shlex
import subprocess

from src.config import config_manager
from src.File import File
from src.media_processing import get_watermarking_command, valid_media_file
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
                        print(
                            f"Warning. Path nor directory nor file. Skipping path: {path}"
                        )

        return valid_media_files
    except OSError as e:
        print(f"Failed to validate paths. Error: {e}")


def watermark_files(media_files: list[File]) -> None:
    for media_file in media_files:
        try:
            watermark_file(media_file)
        except Exception as e:
            print(f"Failed to watermark file: {media_file.path}. Error: {e}")


def watermark_image(file: File) -> None:
    print(f"Watermarking image: {file.path}")

    orientation = file.get_orientation()

    overlay = config_manager.get_image_watermark_overlay(orientation)
    transpose = config_manager.get_image_transpose(orientation)
    watermark_file_path = config_manager.get_watermark_file_path()

    watermark_scaling = file.get_watermark_scaling()
    output_file_path = file.get_output_file_path()

    command = get_watermarking_command(
        input_file_path=file.path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        transpose=transpose,
        watermark_scaling=watermark_scaling,
    )
    subprocess.run(shlex.split(command))


def watermark_video(file: File) -> None:
    print(f"Watermarking video: {file.path}")

    watermark_file_path = config_manager.get_watermark_file_path()
    overlay = config_manager.get_video_watermark_overlay()
    transpose = config_manager.get_video_transpose()

    watermark_scaling = file.get_watermark_scaling()
    output_file_path = file.get_output_file_path()

    command = get_watermarking_command(
        input_file_path=file.path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        transpose=transpose,
        watermark_scaling=watermark_scaling,
    )
    subprocess.run(shlex.split(command))


def watermark_file(file: File) -> None:
    file_type = file.get_type()
    if file_type == FileType.IMAGE:
        watermark_image(file)
    elif file_type == FileType.VIDEO:
        watermark_video(file)
    else:
        print(f"Warning. Unknown file type. Skipping file: {file.path}")
