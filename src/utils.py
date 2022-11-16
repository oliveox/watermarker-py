import os
import shlex
import subprocess

from filetype import filetype

from src.cli import valid_media_file
from src.config import config_manager
from src.constants import constants
from src.media_processing import (
    get_overlay,
    get_image_orientation,
    get_watermarking_command,
    get_watermark_scaling,
    get_watermark_image_ratio,
    get_video_orientation,
)


def process_paths(paths):
    try:
        for path in paths:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file() and valid_media_file(entry.path):
                        watermark_file(entry.path)
                    elif entry.is_dir():
                        process_paths([entry.path])
                    else:
                        print(
                            f"Warning. Path nor directory nor file. Skipping path: {path}"
                        )
    except OSError as e:
        print(f"Failed to process paths. Error: {e}")


def watermark_image(path):
    print(f"Watermarking image: {path}")

    output_file_path = config_manager.get_output_dir_path()
    watermark_file_path = config_manager.get_watermark_file_path()
    watermark_configs = config_manager.get_watermark_positioning_configs()

    overlay = f"[wtrmrk]{get_overlay(**watermark_configs)}"

    orientation = get_image_orientation(path)
    if orientation == constants.PORTRAIT:
        transpose = "[0:v]transpose=2 [mediaFile],"
        overlay = f"[mediaFile]{overlay}"
    else:
        transpose = ""
        overlay = f"[0:v]{overlay}"

    watermark_image_ratio = get_watermark_image_ratio(watermark_file_path)
    watermark_scaling = get_watermark_scaling(
        path=path, orientation=orientation, watermark_image_ratio=watermark_image_ratio
    )
    command = get_watermarking_command(
        input_file_path=path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        transpose=transpose,
        watermark_scaling=watermark_scaling,
    )
    subprocess.run(shlex.split(command))


def watermark_video(path):
    print(f"Watermarking video: {path}")

    output_file_path = config_manager.get_output_dir_path()
    watermark_file_path = config_manager.get_watermark_file_path()
    watermark_configs = config_manager.get_watermark_positioning_configs()

    overlay = f"[0:v][wtrmrk]{get_overlay(**watermark_configs)}"
    transpose = ""
    orientation = get_video_orientation(path)

    watermark_image_ratio = get_watermark_image_ratio(watermark_file_path)
    watermark_scaling = get_watermark_scaling(
        path=path, orientation=orientation, watermark_image_ratio=watermark_image_ratio
    )
    command = get_watermarking_command(
        input_file_path=path,
        watermark_path=watermark_file_path,
        output_file_path=output_file_path,
        overlay=overlay,
        transpose=transpose,
        watermark_scaling=watermark_scaling,
    )
    subprocess.run(shlex.split(command))


def watermark_file(path):
    kind = filetype.guess(path)

    if kind.mime.startswith("image"):
        watermark_image(path)

    elif kind.mime.startswith("video"):
        watermark_video(path)
