import logging
from functools import cache
from typing import Optional

import ffmpeg
from PIL import Image

from src.custom_types import MediaFileOrientation, WidthHeight

logger = logging.getLogger("watermarker")


class MediaUtilsMixin:
    @staticmethod
    @cache
    def get_image_orientation(file_path: str) -> MediaFileOrientation:
        image = Image.open(file_path)
        exif = image.getexif()
        orientation = exif.get(274, None)
        if isinstance(orientation, bytes):
            orientation = orientation.decode()

        if orientation in [5, 6, 7, 8]:
            logger.debug("Found [exif:274] based orientation")
            return MediaFileOrientation.PORTRAIT
        elif orientation is not None:
            logger.debug("Found [exif:274] based orientation")
            return MediaFileOrientation.LANDSCAPE
        else:
            # decide orientation based on image width and height
            # TODO - remove duplication as this is also in get_video_orientation
            # TODO - pass file object as it could already have width and height
            width_height = MediaUtilsMixin.get_media_file_width_height(file_path)
            if not width_height:
                # TODO - flag to choose fallback orienttation if not ffprobe and not wdith height detected ?
                raise Exception("Cannot get width and height for media file", file_path)

            width = width_height["width"]
            height = width_height["height"]
            logger.debug("Found [width:height] based orientation")
            if width >= height:
                return MediaFileOrientation.LANDSCAPE
            else:
                return MediaFileOrientation.PORTRAIT

    @staticmethod
    @cache
    def get_video_orientation(path: str) -> MediaFileOrientation:
        # ffprobe needs to be installed as a package on the client OS
        metadata = ffmpeg.probe(path)
        try:
            rotation = metadata["streams"][0]["tags"]["rotate"]  # noqa: F841
            # TODO - remove this in production
            logger.info(f"!!!!!!!!!! FOUND VIDEO WITH ROTATION: {path}")
            # TODO - find test video with rotatian data
        except IndexError:
            logger.debug("No video stream found")
        except KeyError:
            logger.debug("No [stream:tags:rotate] orientation metadata found")

            try:
                rotation = metadata["streams"][0]["side_data_list"][0]["rotation"]
                logger.debug("Found [stream:side_data_list:rotation] based orientation")

                # check if -90 or 90
                if abs(rotation) / 90 == 1:
                    return MediaFileOrientation.PORTRAIT
                else:
                    return MediaFileOrientation.LANDSCAPE
            except KeyError:
                logger.debug("No [stream:side_data_list:rotation] orientation metadata found")

            # determine based on width height
            width_height = MediaUtilsMixin.get_media_file_width_height(path)
            # TODO - flag to choose fallback orienttation if not ffprobe and not wdith height detected ?
            if not width_height:
                raise Exception("On detect orientation fallback method, cannot get file width and height", path)

            width = width_height["width"]
            height = width_height["height"]
            logger.debug("Found [width:height] based orientation")
            if width >= height:
                return MediaFileOrientation.LANDSCAPE
            else:
                return MediaFileOrientation.PORTRAIT

        return MediaFileOrientation.LANDSCAPE

    @staticmethod
    @cache
    def get_media_file_width_height(file_path: str) -> Optional[WidthHeight]:
        metadata = ffmpeg.probe(file_path)

        try:
            if not metadata or not metadata["streams"][0]["height"] or not metadata["streams"][0]["width"]:
                return None
        except IndexError:
            logger.debug("No video stream found in file")
            return None
        except KeyError:
            logger.debug("No rotation metadata found in file")
            return None

        width = metadata["streams"][0]["width"]
        height = metadata["streams"][0]["height"]

        return {"width": width, "height": height}
