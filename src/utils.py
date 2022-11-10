import os
import shlex
import string
import subprocess

from filetype import filetype

from src.config import config_manager
from src.constants import constants
from src.media_processing import get_overlay, get_image_orientation, get_watermarking_command, get_watermark_scaling, \
    get_watermark_image_ratio, get_video_orientation


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
        print('Cannot guess watermark file type')
        return False

    if not kind.mime.startswith('image'):
        print(f'Watermark file type is not image. Mime: [{kind.mime}]')
        return False

    return True


def valid_prefix(prefix):
    whitelist_chars = string.ascii_letters + string.digits + '_-.'

    if not len(prefix):
        print("Prefix must have at least one character")
        return False

    if not all(c in whitelist_chars for c in prefix):
        print(f"Prefix contains invalid characters. Allowed characters: [{whitelist_chars}]")
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


def valid_media_file(path):
    kind = filetype.guess(path)
    if kind is None:
        print(f"Cannot guess file type for: {path}")
        return False

    if not kind.mime.startswith('image') and not kind.mime.startswith('video'):
        print(f'Invalid media file: [{path}]. Mime: [{kind.mime}]')
        return False

    return True


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
                        print(f"Warning. Path nor directory nor file. Skipping path: {path}")
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
    watermark_scaling = get_watermark_scaling(path=path, orientation=orientation,
                                              watermark_image_ratio=watermark_image_ratio)
    command = get_watermarking_command(input_file_path=path, watermark_path=watermark_file_path,
                                       output_file_path=output_file_path, overlay=overlay, transpose=transpose,
                                       watermark_scaling=watermark_scaling)
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
    watermark_scaling = get_watermark_scaling(path=path, orientation=orientation,
                                              watermark_image_ratio=watermark_image_ratio)
    command = get_watermarking_command(input_file_path=path, watermark_path=watermark_file_path,
                                       output_file_path=output_file_path, overlay=overlay, transpose=transpose,
                                       watermark_scaling=watermark_scaling)
    subprocess.run(shlex.split(command))


def watermark_file(path):
    kind = filetype.guess(path)

    if kind.mime.startswith('image'):
        watermark_image(path)

    elif kind.mime.startswith('video'):
        watermark_video(path)
